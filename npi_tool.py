"""
NPI Registry Search Tool
Searches the NPPES NPI Registry for healthcare provider information.
"""
from typing import Optional, Type
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from utils import get_logger, format_api_error

logger = get_logger(__name__)


class NPISearchInput(BaseModel):
    """Input for the NPISearchTool."""
    first_name: Optional[str] = Field(None, description="The first name of the healthcare provider.")
    last_name: Optional[str] = Field(None, description="The last name of the healthcare provider.")
    state: Optional[str] = Field(None, description="The two-letter state abbreviation (e.g., 'FL', 'NY').")
    npi_number: Optional[str] = Field(None, description="Optional: The 10-digit NPI number for direct lookup.")


class NPISearchTool(BaseTool):
    name: str = "NPI Registry Search"
    description: str = (
        "Search the official NPPES NPI registry for provider NPI, taxonomy (specialty), "
        "and primary practice address."
    )
    args_schema: Type[BaseModel] = NPISearchInput

    def _run(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        state: Optional[str] = None,
        npi_number: Optional[str] = None,
    ) -> str:
        """
        Execute NPI Registry search.
        
        Args:
            first_name: Provider's first name
            last_name: Provider's last name
            state: Two-letter state code
            npi_number: 10-digit NPI number for direct lookup
            
        Returns:
            Formatted search results or error message
        """
        api_url = "https://npiregistry.cms.hhs.gov/api/"
        params = {"version": "2.1", "limit": 5}

        if npi_number:
            params["number"] = npi_number
            search_desc = f"NPI: {npi_number}"
        elif first_name and last_name and state:
            params.update({
                "first_name": first_name,
                "last_name": last_name,
                "state": state
            })
            search_desc = f"{first_name} {last_name} ({state})"
        else:
            return (
                "ERROR: Please provide either 'npi_number' OR a combination of "
                "'first_name', 'last_name', and 'state'."
            )

        logger.info(f"Searching NPI Registry for: {search_desc}")

        try:
            resp = requests.get(api_url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()

            if data.get("result_count", 0) == 0:
                logger.warning(f"No NPI results found for: {search_desc}")
                return f"No matching providers found in NPI Registry for: {search_desc}"

            formatted = []
            for r in data.get("results", []):
                npi = r.get("number", "N/A")
                
                # Get taxonomy (specialty)
                taxonomies = r.get("taxonomies", [])
                tax = taxonomies[0].get("desc", "N/A") if taxonomies else "N/A"
                
                # Prefer PRIMARY address
                addresses = r.get("addresses", [])
                if addresses:
                    primary = next(
                        (a for a in addresses if a.get("address_purpose") == "PRIMARY"),
                        addresses[0]
                    )
                    address_parts = [
                        primary.get("address_1", ""),
                        primary.get("city", ""),
                        primary.get("state", ""),
                        primary.get("postal_code", "")
                    ]
                    address_line = ", ".join(filter(None, address_parts))
                else:
                    address_line = "N/A"
                
                # Get provider name
                basic = r.get("basic", {})
                provider_name = f"{basic.get('first_name', '')} {basic.get('last_name', '')}".strip()
                
                formatted.append(
                    f"✓ FOUND | Name: {provider_name} | NPI: {npi} | "
                    f"Specialty: {tax} | Address: {address_line}"
                )

            logger.info(f"NPI search successful: {len(formatted)} result(s) found")
            return "NPI Search Results:\n" + "\n".join(formatted)

        except requests.exceptions.Timeout:
            error_msg = "ERROR: NPI registry request timed out after 20 seconds."
            logger.error(error_msg)
            return error_msg
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if hasattr(e, 'response') else None
            error_msg = format_api_error("NPI Registry", e, status_code)
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"ERROR: Unexpected error querying NPI registry: {type(e).__name__}: {str(e)}"
            logger.exception(error_msg)
            return error_msg
