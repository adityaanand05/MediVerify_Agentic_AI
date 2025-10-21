from Agent import validation_agent, Reportmaker_agent
from crewai import Task
from npi_tool import NPISearchTool # Assuming 'tools' is the module where npi_tool is defined


npi_search_tool = NPISearchTool()



search_task = Task(

    description=(
        "Search the NPI registry for the healthcare provider with the name: {name} and state: {state} ." 
        "Use the NPI Registry Search tool to find their NPI number, primary practice address, and specialty."
    ),
    expected_output="A list of matching providers, including their Name, NPI, Address, and Taxonomy (Specialty).",
    agent=validation_agent,
    tools=[npi_search_tool],
)


report_task = Task(
    description=(
        "Generate a structured data validation report based on the validated provider list from the Validation Agent. "
        "For each provider entry in the input list, the report must clearly state:\n"
        "  1. The original search query (provider name).\n"
        "  2. The validation status: 'Verified', 'Not Found', or 'Ambiguous Match'.\n"
        "  3. If 'Verified': The single, best-match provider's NPI, Address, and Specialty.\n"
        "  4. If 'Not Found': A note that no matching provider was located in the database.\n"
        "  5. If 'Ambiguous Match': A list of the multiple potential providers that were returned, including their NPIs for review.\n"
        "The report should begin with an executive summary quantifying the results (e.g., 'X verified, Y not found, Z ambiguous')."
    ),
    expected_output=(
        "A comprehensive Markdown report titled 'Healthcare Provider Validation Report'. "
        "The report must be well-structured with clear headings, use bullet points for lists, and be saved to the specified output file. "
        "The data should be presented in a table for the 'Verified' providers for maximum clarity."
    ),
    tools=[npi_search_tool], 
    agent=Reportmaker_agent,
    async_execution=False,
    output_file='./reports/new_report.md' 
)