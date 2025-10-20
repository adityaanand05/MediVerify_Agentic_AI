from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
import requests


class NPISearchInput(BaseModel):
    """Input for the NPISearchTool."""
    first_name: str = Field(..., description="The first name of the healthcare provider.")
    last_name: str = Field(..., description="The last name of the healthcare provider.")
    state: str = Field(..., description="The two-letter state abbreviation (e.g., 'FL', 'NY').")
    npi_number: str = Field(None, description="Optional: The 10-digit NPI number for direct lookup.")

class NPISearchTool(BaseTool):
    name: str = "NPI Registry Search"
    description: str = (
        "A specialized tool for searching the official NPPES National Provider Identifier (NPI) registry. "
        "Use this tool to find a provider's NPI, address, and taxonomy based on their name and location."
    )
    args_schema: Type[BaseModel] = NPISearchInput
    
    def _run(self, first_name: str, last_name: str, state: str, npi_number: str = None) -> str:

        api_url = "https://npiregistry.cms.hhs.gov/api/"
        

        params = {
            "version": "2.1",
            "limit": 5, 
        }
        
  
        if npi_number:
            params['number'] = npi_number
        else:
            
            if first_name and last_name and state:
                params['first_name'] = first_name
                params['last_name'] = last_name
                params['state'] = state
            else:
                return "Error: NPI Search requires either 'npi_number' OR a combination of 'first_name', 'last_name', and 'state'."


        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status() 
            data = response.json()
            
          
            if data.get('result_count', 0) > 0:
                results_summary = []
                for result in data['results']:
                  
                    npi = result.get('number', 'N/A')
                    taxonomies = result.get('taxonomies', [{}])
                    taxonomy_desc = taxonomies[0].get('desc', 'N/A')
                    
                    addresses = result.get('addresses', [{}])
                    primary_address = next((a for a in addresses if a.get('address_purpose') == 'PRIMARY'), addresses[0])

                    address_line = f"{primary_address.get('address_1', '')}, {primary_address.get('city', '')}, {primary_address.get('state', '')}"
                    
                    results_summary.append(f"NPI: {npi}, Specialty: {taxonomy_desc}, Primary Address: {address_line}")
                    
                return "NPI Search Results: " + " | ".join(results_summary)
            else:
                return "NPI Search Tool found no providers matching the criteria."
            
        except requests.exceptions.RequestException as e:
            return f"An error occurred while accessing the NPI database (HTTP/Network Error): {e}"
        except Exception as e:
            return f"An unexpected error occurred during API processing: {e}"