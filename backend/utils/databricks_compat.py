"""
Databricks SDK Compatibility Layer

This module handles different versions of the Databricks SDK and provides
a consistent interface regardless of the SDK version.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try to import the WorkspaceClient
try:
    from databricks.sdk import WorkspaceClient
    DATABRICKS_SDK_AVAILABLE = True
    logger.info("Databricks SDK imported successfully")
except ImportError as e:
    logger.error(f"Failed to import Databricks SDK: {e}")
    WorkspaceClient = None
    DATABRICKS_SDK_AVAILABLE = False

# Handle different error classes across SDK versions
DatabricksError = Exception  # Default fallback

if DATABRICKS_SDK_AVAILABLE:
    # Try different import paths for DatabricksError
    error_import_paths = [
        'databricks.sdk.errors.DatabricksError',
        'databricks.sdk.core.DatabricksError', 
        'databricks.sdk.DatabricksError',
        'databricks.errors.DatabricksError'
    ]
    
    for import_path in error_import_paths:
        try:
            module_path, class_name = import_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            DatabricksError = getattr(module, class_name)
            logger.info(f"Successfully imported DatabricksError from {import_path}")
            break
        except (ImportError, AttributeError):
            continue
    else:
        logger.warning("Could not import DatabricksError, using generic Exception")


def create_workspace_client(host: Optional[str] = None, token: Optional[str] = None) -> Any:
    """
    Create a WorkspaceClient with proper error handling.
    
    Args:
        host: Databricks workspace host URL
        token: Databricks access token
        
    Returns:
        WorkspaceClient instance
        
    Raises:
        ImportError: If Databricks SDK is not available
        Exception: If client creation fails
    """
    if not DATABRICKS_SDK_AVAILABLE:
        raise ImportError("Databricks SDK is not available")
    
    try:
        if host and token:
            logger.info(f"Creating WorkspaceClient with explicit credentials for {host}")
            return WorkspaceClient(host=host, token=token)
        else:
            logger.info("Creating WorkspaceClient with default authentication")
            return WorkspaceClient()
    except Exception as e:
        logger.error(f"Failed to create WorkspaceClient: {e}")
        raise


def is_rate_limit_error(error: Exception) -> bool:
    """
    Check if an error is a rate limiting error across different SDK versions.
    
    Args:
        error: The exception to check
        
    Returns:
        bool: True if it's a rate limit error
    """
    # Check various ways rate limit errors might be indicated
    checks = [
        hasattr(error, 'http_status_code') and error.http_status_code == 429,
        hasattr(error, 'status_code') and error.status_code == 429,
        '429' in str(error),
        'rate limit' in str(error).lower(),
        'too many requests' in str(error).lower()
    ]
    
    return any(checks)


def get_sdk_version() -> Optional[str]:
    """
    Get the version of the Databricks SDK if available.
    
    Returns:
        str: SDK version or None if not available
    """
    if not DATABRICKS_SDK_AVAILABLE:
        return None
    
    try:
        import databricks.sdk
        return getattr(databricks.sdk, '__version__', 'unknown')
    except Exception:
        return 'unknown'


# Log SDK information on import
if DATABRICKS_SDK_AVAILABLE:
    sdk_version = get_sdk_version()
    logger.info(f"Databricks SDK compatibility layer initialized (version: {sdk_version})")
else:
    logger.warning("Databricks SDK not available - some features will be disabled")
