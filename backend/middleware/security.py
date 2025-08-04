import time
import logging
from typing import Dict, Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict, deque
import asyncio
import uuid

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware to prevent API abuse"""
    
    def __init__(self, app, calls: int = 100, period: int = 3600):
        super().__init__(app)
        self.calls = calls  # max calls per period
        self.period = period  # period in seconds
        self.clients = defaultdict(lambda: deque())
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Max {self.calls} requests per {self.period} seconds",
                    "retry_after": self.period
                }
            )
        
        # Add request to client history
        self._add_request(client_ip)
        
        response = await call_next(request)
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit"""
        now = time.time()
        client_requests = self.clients[client_ip]
        
        # Remove old requests outside the time window
        while client_requests and client_requests[0] < now - self.period:
            client_requests.popleft()
        
        return len(client_requests) >= self.calls
    
    def _add_request(self, client_ip: str):
        """Add current request to client history"""
        self.clients[client_ip].append(time.time())

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Structured logging for all requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "")
            }
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "process_time": round(process_time, 3)
                }
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "correlation_id": correlation_id,
                    "error": str(e),
                    "process_time": round(process_time, 3)
                },
                exc_info=True
            )
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Additional input validation and sanitization"""
    
    SUSPICIOUS_PATTERNS = [
        r'<script.*?>.*?</script>',  # XSS
        r'javascript:',  # XSS
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # Code injection
        r'union\s+select',  # SQL injection
        r'drop\s+table',  # SQL injection
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Check for suspicious patterns in query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                if self._contains_suspicious_content(value):
                    logger.warning(
                        "Suspicious input detected",
                        extra={
                            "correlation_id": getattr(request.state, 'correlation_id', 'unknown'),
                            "parameter": key,
                            "value": value[:100],  # Log first 100 chars only
                            "client_ip": self._get_client_ip(request)
                        }
                    )
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "error": "Invalid input detected",
                            "detail": "Request contains suspicious content"
                        }
                    )
        
        return await call_next(request)
    
    def _contains_suspicious_content(self, content: str) -> bool:
        """Check if content contains suspicious patterns"""
        import re
        content_lower = content.lower()
        
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host

# API Key validation for additional security
class APIKeyValidator:
    """Validate API keys for sensitive endpoints"""
    
    def __init__(self, valid_keys: Optional[Dict[str, str]] = None):
        self.valid_keys = valid_keys or {}
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return associated user/client"""
        if api_key in self.valid_keys:
            return self.valid_keys[api_key]
        return None

# Enhanced error handler
async def validation_exception_handler(request: Request, exc):
    """Handle Pydantic validation errors with structured response"""
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    
    logger.warning(
        "Validation error",
        extra={
            "correlation_id": correlation_id,
            "errors": exc.errors(),
            "client_ip": request.headers.get("X-Forwarded-For", request.client.host)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "detail": "The provided data is invalid",
            "correlation_id": correlation_id,
            "errors": exc.errors()
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with structured response"""
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    
    logger.warning(
        "HTTP exception",
        extra={
            "correlation_id": correlation_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "client_ip": request.headers.get("X-Forwarded-For", request.client.host)
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request failed",
            "detail": exc.detail,
            "correlation_id": correlation_id
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    correlation_id = getattr(request.state, 'correlation_id', str(uuid.uuid4()))
    
    logger.error(
        "Unexpected error",
        extra={
            "correlation_id": correlation_id,
            "error": str(exc),
            "client_ip": request.headers.get("X-Forwarded-For", request.client.host)
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "correlation_id": correlation_id
        }
    )