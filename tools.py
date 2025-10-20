
from crewai_tools import APITool, SerperDevTool

# Initialize the API Tool for NPI searches
npi_tool = APITool(
    name="NPI Registry Search",
    description="Search the National Provider Identifier registry for healthcare providers",
    config={
        "base_url": "https://npiregistry.cms.hhs.gov/api/?version=2.1",
        "params": {
            "version": "2.1",
            "limit": 10
        }
    }
)

# Optional: For broader searches
search_tool = SerperDevTool()
