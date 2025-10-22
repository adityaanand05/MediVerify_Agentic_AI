"""
Utility Functions
Provides logging, retry logic, and validation helpers.
"""
import logging
import sys
from typing import Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# Valid US state codes
VALID_STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
}


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only add handler if logger doesn't have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def create_retry_session(
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: tuple = (500, 502, 503, 504)
) -> requests.Session:
    """
    Create a requests session with retry logic.
    
    Args:
        retries: Number of retry attempts
        backoff_factor: Backoff factor for retries
        status_forcelist: HTTP status codes to retry
        
    Returns:
        Configured requests Session
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def validate_state_code(state: str) -> bool:
    """
    Validate if the state code is valid.
    
    Args:
        state: Two-letter state code
        
    Returns:
        True if valid, False otherwise
    """
    if not state or not isinstance(state, str):
        return False
    return state.upper() in VALID_STATE_CODES


def normalize_state_code(state: str) -> str:
    """
    Normalize state code to uppercase.
    
    Args:
        state: State code to normalize
        
    Returns:
        Uppercase state code
    """
    return state.upper().strip() if state else ""


def sanitize_name(name: str) -> str:
    """
    Sanitize provider name for API calls.
    
    Args:
        name: Name to sanitize
        
    Returns:
        Sanitized name
    """
    if not name:
        return ""
    return name.strip().title()


def format_api_error(
    api_name: str,
    error: Exception,
    status_code: Optional[int] = None
) -> str:
    """
    Format API error message consistently.
    
    Args:
        api_name: Name of the API
        error: Exception that occurred
        status_code: HTTP status code if available
        
    Returns:
        Formatted error message
    """
    if status_code:
        return f"ERROR: {api_name} API returned HTTP {status_code}: {str(error)}"
    return f"ERROR: {api_name} API error: {str(error)}"
