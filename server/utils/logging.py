import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import json
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log request details
        start_time = time.time()
        
        # Get request body if it exists
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8')
                    # Try to parse as JSON for better logging
                    try:
                        body_json = json.loads(body)
                        body = json.dumps(body_json, indent=2)
                    except:
                        pass  # Keep as string if not JSON
            except Exception as e:
                logger.warning(f"Could not read request body: {e}")
        
        # Log request
        logger.info(f"REQUEST: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        if body:
            logger.info(f"Request Body: {body}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Get response body if possible
        response_body = None
        try:
            if hasattr(response, 'body'):
                response_body = response.body.decode('utf-8')
                # Try to parse as JSON for better logging
                try:
                    response_json = json.loads(response_body)
                    response_body = json.dumps(response_json, indent=2)
                except:
                    pass
        except Exception as e:
            logger.warning(f"Could not read response body: {e}")
        
        # Log response
        logger.info(f"RESPONSE: {response.status_code} - {process_time:.3f}s")
        if response_body:
            logger.info(f"Response Body: {response_body}")
        
        return response

def log_api_call(func_name: str, **kwargs):
    """Decorator to log API function calls with parameters"""
    def decorator(func):
        async def wrapper(*args, **func_kwargs):
            logger.info(f"API CALL: {func_name}")
            logger.info(f"Parameters: {json.dumps(func_kwargs, indent=2, default=str)}")
            
            try:
                result = await func(*args, **func_kwargs)
                logger.info(f"API SUCCESS: {func_name}")
                return result
            except Exception as e:
                logger.error(f"API ERROR: {func_name} - {str(e)}")
                logger.error(f"Error details: {type(e).__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

def log_error(error: Exception, context: str = "", **kwargs):
    """Log errors with context and additional information"""
    logger.error(f"ERROR in {context}: {type(error).__name__}: {str(error)}")
    if kwargs:
        logger.error(f"Additional context: {json.dumps(kwargs, indent=2, default=str)}")
    
    # Log the full traceback for debugging
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
