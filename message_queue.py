"""
Message Queue System for Genie to Chart POC

This module provides a queuing system to handle concurrent message processing
from different conversations, preventing conflicts and connection issues.
"""

import asyncio
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import threading
from queue import Queue, Empty


class MessageStatus(Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class QueuedMessage:
    """Represents a message in the processing queue"""
    id: str
    conversation_id: str
    session_id: str
    user_message: str
    timestamp: str
    status: MessageStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_started_at: Optional[str] = None
    processing_completed_at: Optional[str] = None


class MessageQueue:
    """Thread-safe message queue for processing conversation messages"""
    
    def __init__(self, max_concurrent_workers: int = 2, max_queue_size: int = 100):
        self.queue = Queue(maxsize=max_queue_size)
        self.pending_messages: Dict[str, QueuedMessage] = {}
        self.max_concurrent_workers = max_concurrent_workers
        self.current_workers = 0
        self.workers = []
        self.running = False
        self.lock = threading.Lock()
        
        # Callbacks for processing messages
        self.message_processor: Optional[Callable] = None
        self.status_callback: Optional[Callable] = None
        
        logger.info(f"MessageQueue initialized with {max_concurrent_workers} max workers")
    
    def set_message_processor(self, processor: Callable):
        """Set the function that will process messages"""
        self.message_processor = processor
    
    def set_status_callback(self, callback: Callable):
        """Set callback for status updates"""
        self.status_callback = callback
    
    def start(self):
        """Start the message processing workers"""
        if self.running:
            return
            
        self.running = True
        
        # Start worker threads
        for i in range(self.max_concurrent_workers):
            worker = threading.Thread(target=self._worker, name=f"MessageWorker-{i}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {len(self.workers)} message processing workers")
    
    def stop(self):
        """Stop the message processing workers"""
        if not self.running:
            return
            
        self.running = False
        
        # Signal workers to stop by putting sentinel values
        for _ in self.workers:
            self.queue.put(None)
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
        logger.info("Stopped all message processing workers")
    
    def add_message(self, conversation_id: str, session_id: str, user_message: str) -> str:
        """Add a message to the processing queue"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        queued_message = QueuedMessage(
            id=message_id,
            conversation_id=conversation_id,
            session_id=session_id,
            user_message=user_message,
            timestamp=timestamp,
            status=MessageStatus.QUEUED
        )
        
        with self.lock:
            self.pending_messages[message_id] = queued_message
        
        try:
            self.queue.put(message_id, timeout=1.0)  # 1 second timeout
            logger.info(f"Queued message {message_id} for conversation {conversation_id}")
            
            # Notify status callback
            if self.status_callback:
                try:
                    self.status_callback(message_id, MessageStatus.QUEUED, None, None)
                except Exception as e:
                    logger.warning(f"Status callback failed: {e}")
            
            return message_id
        except Exception as e:
            # Remove from pending if we couldn't queue it
            with self.lock:
                if message_id in self.pending_messages:
                    del self.pending_messages[message_id]
            
            logger.error(f"Failed to queue message: {e}")
            raise Exception("Message queue is full. Please try again later.")
    
    def get_message_status(self, message_id: str) -> Optional[QueuedMessage]:
        """Get the status of a queued message"""
        with self.lock:
            return self.pending_messages.get(message_id)
    
    def cancel_message(self, message_id: str) -> bool:
        """Cancel a queued message (only works if not yet processing)"""
        with self.lock:
            if message_id in self.pending_messages:
                message = self.pending_messages[message_id]
                if message.status == MessageStatus.QUEUED:
                    message.status = MessageStatus.CANCELLED
                    logger.info(f"Cancelled message {message_id}")
                    return True
        return False
    
    def get_queue_info(self) -> Dict[str, Any]:
        """Get information about the queue state"""
        with self.lock:
            queue_size = self.queue.qsize()
            total_pending = len(self.pending_messages)
            
            status_counts = {}
            for message in self.pending_messages.values():
                status = message.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'queue_size': queue_size,
            'total_pending': total_pending,
            'current_workers': self.current_workers,
            'max_workers': self.max_concurrent_workers,
            'status_counts': status_counts,
            'running': self.running
        }
    
    def _worker(self):
        """Worker thread function for processing messages"""
        worker_name = threading.current_thread().name
        logger.info(f"Message worker {worker_name} started")
        
        while self.running:
            try:
                # Get message ID from queue (blocks until available)
                message_id = self.queue.get(timeout=1.0)
                
                # Check for sentinel value (stop signal)
                if message_id is None:
                    break
                
                # Get the message details
                with self.lock:
                    if message_id not in self.pending_messages:
                        continue
                    
                    message = self.pending_messages[message_id]
                    
                    # Skip if cancelled
                    if message.status == MessageStatus.CANCELLED:
                        continue
                    
                    # Mark as processing
                    message.status = MessageStatus.PROCESSING
                    message.processing_started_at = datetime.now(timezone.utc).isoformat()
                    self.current_workers += 1
                
                logger.info(f"Worker {worker_name} processing message {message_id} for conversation {message.conversation_id}")
                
                # Notify status callback
                if self.status_callback:
                    try:
                        self.status_callback(message_id, MessageStatus.PROCESSING, None, None)
                    except Exception as e:
                        logger.warning(f"Status callback failed: {e}")
                
                try:
                    # Process the message
                    if self.message_processor:
                        result = self.message_processor(
                            message.conversation_id,
                            message.session_id, 
                            message.user_message
                        )
                        
                        # Mark as completed
                        with self.lock:
                            if message_id in self.pending_messages:
                                message = self.pending_messages[message_id]
                                message.status = MessageStatus.COMPLETED
                                message.result = result
                                message.processing_completed_at = datetime.now(timezone.utc).isoformat()
                        
                        logger.info(f"Worker {worker_name} completed message {message_id}")
                        
                        # Notify status callback
                        if self.status_callback:
                            try:
                                self.status_callback(message_id, MessageStatus.COMPLETED, result, None)
                            except Exception as e:
                                logger.warning(f"Status callback failed: {e}")
                    
                    else:
                        raise Exception("No message processor configured")
                        
                except Exception as e:
                    # Mark as failed
                    error_msg = str(e)
                    with self.lock:
                        if message_id in self.pending_messages:
                            message = self.pending_messages[message_id]
                            message.status = MessageStatus.FAILED
                            message.error = error_msg
                            message.processing_completed_at = datetime.now(timezone.utc).isoformat()
                    
                    logger.error(f"Worker {worker_name} failed to process message {message_id}: {error_msg}")
                    
                    # Notify status callback
                    if self.status_callback:
                        try:
                            self.status_callback(message_id, MessageStatus.FAILED, None, error_msg)
                        except Exception as e:
                            logger.warning(f"Status callback failed: {e}")
                
                finally:
                    # Mark worker as available
                    with self.lock:
                        self.current_workers -= 1
                    
                    # Clean up old completed/failed messages (keep last 100)
                    self._cleanup_old_messages()
                    
                    self.queue.task_done()
                    
            except Empty:
                # Timeout waiting for message, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_name} encountered unexpected error: {e}")
                continue
        
        logger.info(f"Message worker {worker_name} stopped")
    
    def _cleanup_old_messages(self, max_keep: int = 100):
        """Clean up old completed/failed messages to prevent memory leak"""
        with self.lock:
            if len(self.pending_messages) <= max_keep:
                return
            
            # Sort by completion time, keep the most recent
            completed_messages = [
                (msg_id, msg) for msg_id, msg in self.pending_messages.items()
                if msg.status in [MessageStatus.COMPLETED, MessageStatus.FAILED, MessageStatus.CANCELLED]
                and msg.processing_completed_at
            ]
            
            if len(completed_messages) > max_keep // 2:
                # Sort by completion time (oldest first)
                completed_messages.sort(key=lambda x: x[1].processing_completed_at)
                
                # Remove oldest messages
                to_remove = len(completed_messages) - (max_keep // 2)
                for i in range(to_remove):
                    msg_id = completed_messages[i][0]
                    del self.pending_messages[msg_id]
                
                logger.debug(f"Cleaned up {to_remove} old messages from queue")


# Global message queue instance
message_queue = MessageQueue(max_concurrent_workers=2, max_queue_size=50)
