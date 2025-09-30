"""
Simplified Databricks Genie Client for POC
"""
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import DatabricksError
from loguru import logger
from ..core.config import settings


@dataclass
class GenieQueryResult:
    """Result from a Genie query"""
    sql_query: str
    data: List[List[Any]]
    columns: List[str]
    raw_response: str


class GenieClient:
    """Simplified client for interacting with Databricks Genie"""
    
    def __init__(self, workspace_client: Optional[WorkspaceClient] = None, space_id: Optional[str] = None):
        self.workspace_client = workspace_client or WorkspaceClient(
            host=settings.databricks_host,
            token=settings.databricks_token
        )
        self.space_id = space_id or settings.genie_space_id
        
    def _exponential_backoff(self, func, *args, max_retries: int = None, base_delay: float = None, **kwargs):
        """Execute function with exponential backoff for rate limiting"""
        max_retries = max_retries or settings.max_retries
        base_delay = base_delay or settings.initial_backoff
        
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except DatabricksError as e:
                # Check if it's a rate limit error (429)
                if hasattr(e, 'http_status_code') and e.http_status_code == 429:
                    wait_time = min(
                        base_delay * (settings.backoff_multiplier ** retries),
                        settings.max_backoff
                    )
                    # Add jitter
                    wait_time += random.uniform(0, 0.1 * wait_time)
                    
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    # For other errors, don't retry
                    raise
        raise Exception(f"Max retries ({max_retries}) exceeded for function {func.__name__}")
    
    def list_spaces(self) -> List[Dict[str, Any]]:
        """List all accessible Genie spaces"""
        try:
            spaces = self._exponential_backoff(self.workspace_client.genie.list_spaces)
            return [
                {
                    "space_id": space.space_id,
                    "title": space.title,
                    "description": getattr(space, 'description', None)
                }
                for space in spaces.spaces
            ]
        except Exception as e:
            logger.error(f"Failed to list Genie spaces: {e}")
            raise
    
    def get_default_space_id(self) -> str:
        """Get the first available space ID if none is specified"""
        if self.space_id:
            return self.space_id
        
        spaces = self.list_spaces()
        if not spaces:
            raise ValueError("No Genie spaces found. Please create a Genie space first.")
        
        # Use the first available space
        default_space_id = spaces[0]["space_id"]
        logger.info(f"Using default space: {spaces[0]['title']} ({default_space_id})")
        return default_space_id
    
    def query_data(self, question: str) -> GenieQueryResult:
        """Query data using Genie and return structured results"""
        try:
            # Get space ID
            space_id = self.get_default_space_id()
            
            # Start conversation with Genie
            result = self._exponential_backoff(
                self.workspace_client.genie.start_conversation_and_wait,
                space_id,
                question
            )
            
            # Extract SQL query and results
            sql_query = ""
            data = []
            columns = []
            raw_response = ""
            
            if hasattr(result, 'attachments') and result.attachments:
                for attachment in result.attachments:
                    if hasattr(attachment, 'text') and attachment.text:
                        raw_response += attachment.text.content + "\n"
                    elif hasattr(attachment, 'query') and attachment.query:
                        # Get the SQL query
                        sql_query = attachment.query.query
                        
                        # Fetch actual query results using Genie's built-in method
                        if hasattr(attachment.query, 'statement_id') and attachment.query.statement_id:
                            try:
                                # Get message_id and attachment_id for the Genie method
                                message_id = getattr(result, 'message_id', None)
                                attachment_id = getattr(attachment, 'attachment_id', None)
                                
                                if message_id and attachment_id:
                                    # Use Genie's built-in method to get query results
                                    query_result = self._exponential_backoff(
                                        self.workspace_client.genie.get_message_attachment_query_result,
                                        space_id,
                                        result.conversation_id,
                                        message_id,
                                        attachment_id
                                    )
                                    
                                    if (query_result and 
                                        hasattr(query_result, 'statement_response') and 
                                        query_result.statement_response and
                                        hasattr(query_result.statement_response, 'result') and
                                        query_result.statement_response.result and
                                        hasattr(query_result.statement_response.result, 'data_array') and
                                        query_result.statement_response.result.data_array):
                                        
                                        data = query_result.statement_response.result.data_array
                                        
                                        # Get column information from the manifest
                                        if (hasattr(query_result.statement_response, 'manifest') and 
                                            query_result.statement_response.manifest and 
                                            hasattr(query_result.statement_response.manifest, 'schema') and
                                            query_result.statement_response.manifest.schema and
                                            hasattr(query_result.statement_response.manifest.schema, 'columns')):
                                            columns = [col.name for col in query_result.statement_response.manifest.schema.columns]
                                        
                                        # If no column info, use generic column names
                                        if not columns and data:
                                            columns = [f"Column_{i+1}" for i in range(len(data[0]))]
                                        
                            except Exception as e:
                                logger.warning(f"Failed to fetch query results: {e}")
            
            return GenieQueryResult(
                sql_query=sql_query,
                data=data,
                columns=columns,
                raw_response=raw_response.strip()
            )
            
        except Exception as e:
            logger.error(f"Failed to query Genie: {e}")
            raise

