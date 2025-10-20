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
        "Analyze the list of providers found by the Validation Agent. "
        "Use this validated data to compile a comprehensive data validation report. "
        "The report must summarize the findings, highlight any discrepancies (if a name was searched and no data was found, or if multiple providers were returned), and list the final, verified NPI, Address, and Specialty."
    ),
    expected_output='A detailed report summarizing the validation and enrichment findings for the specified healthcare provider, saved to the output file.',
    tools=[], 
    agent=Reportmaker_agent,
    async_execution=False,
    output_file='new_report.md'
)