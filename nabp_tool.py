"""
NABP Pharmacist License Validation Tool
Validates pharmacist licenses through the NABP e-Profile system.
"""
from typing import Optional, Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from config import Config
from utils import get_logger, format_api_error

logger = get_logger(__name__)


class NABPValidationInput(BaseModel):
    """Input for NABP Validation."""
    first_name: Optional[str] = Field(None, description="Pharmacist's first name.")
    last_name: Optional[str] = Field(None, description="Pharmacist's last name.")
    license_number: Optional[str] = Field(None, description="Pharmacist's license number (optional).")
    state: Optional[str] = Field(None, description="Two-letter state code where licensed.")


class NABPValidationTool(BaseTool):
    name: str = "NABP Pharmacist License Validation"
    description: str = "Validates pharmacist licenses through the NABP e-Profile system."
    args_schema: Type[BaseModel] = NABPValidationInput

    def _run(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        license_number: Optional[str] = None,
        state: Optional[str] = None,
    ) -> str:
        """
        Execute NABP license validation.
        
        Args:
            first_name: Pharmacist's first name
            last_name: Pharmacist's last name
            license_number: License number
            state: Two-letter state code
            
        Returns:
            Validation results or error message
        """
        base_url = Config.NABP_BASE_URL
        api_key = Config.NABP_API_KEY
        
        search_desc = f"{first_name or ''} {last_name or ''}, License: {license_number or 'N/A'} ({state or 'N/A'})"
        logger.info(f"Validating NABP license for: {search_desc}")

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        # Build payload with camelCase (NABP API standard)
        payload = {}
        if first_name:
            payload["firstName"] = first_name
        if last_name:
            payload["lastName"] = last_name
        if license_number:
            payload["licenseNumber"] = license_number
        if state:
            payload["state"] = state.upper()

        if not payload:
            return "ERROR: At least one identifying field (first_name/last_name/license_number/state) is required."

        try:
            resp = requests.post(base_url, json=payload, headers=headers, timeout=25)
            resp.raise_for_status()
            data = resp.json()

            # Check validation status
            valid = (
                data.get("valid") or 
                data.get("is_valid") or 
                data.get("status") in ["VALIDATED", "VALID", "Active"]
            )

            if valid:
                # Extract license information
                license_info = data.get("license", {}) or {}
                status = (
                    license_info.get("status") or 
                    data.get("licenseStatus") or 
                    data.get("license_status") or 
                    "Active"
                )
                exp = (
                    license_info.get("expiration_date") or 
                    data.get("expirationDate") or 
                    "Unknown"
                )
                profile_info = data.get("profile", {}) or {}
                profile_id = (
                    profile_info.get("e_profile_id") or 
                    data.get("eProfileId") or 
                    "N/A"
                )

                logger.info(f"NABP validation successful for: {search_desc}")
                
                return (
                    f"✓ VALID LICENSE (NABP Verified)\n"
                    f"  Name: {first_name or ''} {last_name or ''}\n"
                    f"  License: {license_number or 'N/A'} ({state or 'N/A'})\n"
                    f"  Status: {status}\n"
                    f"  Expires: {exp}\n"
                    f"  eProfile ID: {profile_id}"
                )

            # If not valid
            message = data.get("message") or data.get("error") or "License not validated."
            logger.warning(f"NABP validation failed for {search_desc}: {message}")
            
            return (
                f"✗ LICENSE NOT VERIFIED\n"
                f"  Name: {first_name or ''} {last_name or ''}\n"
                f"  License: {license_number or 'N/A'} ({state or 'N/A'})\n"
                f"  Reason: {message}"
            )

        except requests.exceptions.Timeout:
            error_msg = "ERROR: NABP API request timed out after 25 seconds."
            logger.error(error_msg)
            return error_msg
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            
            if status_code == 401:
                error_msg = "ERROR: NABP authentication failed (401). Check NABP_API_KEY in .env file."
            elif status_code == 404:
                error_msg = "ERROR: NABP resource not found (404). Pharmacist may not be registered."
            else:
                error_msg = format_api_error("NABP", e, status_code)
            
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"ERROR: Unexpected error calling NABP API: {type(e).__name__}: {str(e)}"
            logger.exception(error_msg)
            return error_msg
