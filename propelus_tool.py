"""
Propelus License Verification Tool
Verifies healthcare provider licenses using Propelus Primary Source Verification API.
"""
from typing import Optional, Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, validator

from config import Config
from utils import (
    create_retry_session,
    get_logger,
    validate_state_code,
    normalize_state_code,
    format_api_error
)

logger = get_logger(__name__)


class PropelusLicenseInput(BaseModel):
    """Input schema for Propelus license verification."""
    
    first_name: str = Field(..., description="Provider's first name")
    last_name: str = Field(..., description="Provider's last name")
    state: str = Field(..., description="License issuing state (2-letter code)")
    license_number: str = Field(..., description="License number for verification")
    
    @validator('state')
    def validate_state(cls, v):
        """Validate and normalize state code."""
        if not validate_state_code(v):
            raise ValueError('State must be a valid 2-letter code')
        return normalize_state_code(v)
    
    @validator('first_name', 'last_name')
    def validate_name(cls, v):
        """Validate name fields."""
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v.strip()
    
    @validator('license_number')
    def validate_license(cls, v):
        """Validate license number."""
        if not v or len(v.strip()) < 3:
            raise ValueError('License number must be at least 3 characters')
        return v.strip()


class PropelusLicenseVerificationTool(BaseTool):
    """
    Tool for verifying healthcare provider licenses through Propelus.
    
    Performs primary source verification of healthcare provider licenses
    using the Propelus API, which connects to over 4,800 license,
    certification, and registration sources.
    """
    
    name: str = "Propelus License Verification"
    description: str = (
        "Verifies healthcare provider licenses using Propelus Primary Source "
        "Verification API. Checks license validity, status, and board information "
        "from authoritative sources."
    )
    args_schema: Type[BaseModel] = PropelusLicenseInput
    
    def _run(
        self,
        first_name: str,
        last_name: str,
        state: str,
        license_number: str
    ) -> str:
        """
        Execute Propelus license verification.
        
        Args:
            first_name: Provider's first name
            last_name: Provider's last name
            state: Two-letter state code
            license_number: License number
            
        Returns:
            Verification results or error message
        """
        search_desc = f"{first_name} {last_name}, License: {license_number} ({state})"
        logger.info(f"Verifying Propelus license for: {search_desc}")
        
        # Get API key from config
        api_key = Config.PROPELUS_API_KEY
        
        if not api_key:
            error_msg = "ERROR: PROPELUS_API_KEY not configured in .env file"
            logger.error(error_msg)
            return error_msg
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "state": state,
            "license_number": license_number
        }
        
        # Create session with retry logic
        session = create_retry_session(
            retries=Config.MAX_RETRIES,
            backoff_factor=Config.RETRY_BACKOFF_FACTOR
        )
        
        try:
            response = session.post(
                Config.PROPELUS_BASE_URL,
                json=payload,
                headers=headers,
                timeout=Config.API_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("verified", False):
                status = data.get("status", "Active")
                board = data.get("board", "N/A")
                issue_date = data.get("issue_date", "Unknown")
                expiration = data.get("expiration_date", "Unknown")
                discipline = data.get("disciplinary_actions", [])
                
                logger.info(f"Propelus verification successful for: {search_desc}")
                
                result = (
                    f"✓ VALID LICENSE (Propelus Verified)\n"
                    f"  Name: {first_name} {last_name}\n"
                    f"  License Number: {license_number}\n"
                    f"  State: {state}\n"
                    f"  Status: {status}\n"
                    f"  Board: {board}\n"
                    f"  Issue Date: {issue_date}\n"
                    f"  Expiration: {expiration}"
                )
                
                if discipline:
                    result += f"\n  ⚠ Disciplinary Actions: {len(discipline)}"
                
                return result
            else:
                reason = data.get("reason", "License not found or inactive")
                logger.warning(f"Propelus verification failed for {search_desc}: {reason}")
                
                return (
                    f"✗ LICENSE NOT VERIFIED\n"
                    f"  Name: {first_name} {last_name}\n"
                    f"  License: {license_number} ({state})\n"
                    f"  Reason: {reason}"
                )
        
        except requests.exceptions.Timeout:
            error_msg = f"ERROR: Propelus API request timed out after {Config.API_TIMEOUT} seconds"
            logger.error(error_msg)
            return error_msg
        
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            
            if status_code == 401:
                error_msg = "ERROR: Propelus authentication failed (401). Check PROPELUS_API_KEY in .env file"
            elif status_code == 429:
                error_msg = "ERROR: Propelus rate limit exceeded (429). Please try again later"
            else:
                error_msg = format_api_error("Propelus", e, status_code)
            
            logger.error(error_msg)
            return error_msg
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"ERROR: Propelus API connection failed: {str(e)}"
            logger.error(error_msg)
            return error_msg
        
        except Exception as e:
            error_msg = f"ERROR: Unexpected error in Propelus verification: {type(e).__name__}: {str(e)}"
            logger.exception(error_msg)
            return error_msg
        
        finally:
            # Close session after use
            session.close()
