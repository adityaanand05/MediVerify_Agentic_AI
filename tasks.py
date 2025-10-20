from Agent import validation_agent , Reportmaker_agent
from crewai import Task
from tools import npi_tool
search_task = Task(
    description="Find healthcare providers name searched by user using NPI API",
    expected_output="List of providers with their NPI numbers, addresses, and specialties",
    agent=validation_agent,
    tools=[npi_tool],
)


report_task = Task(
  description=(
    "get the info from the site on the name{name}."
  ),
  expected_output='A detailed report summarizing the validation and enrichment findings for the specified healthcare provider.',
  tools=[npi_tool],
  agent=Reportmaker_agent,
  async_execution=False,
  output_file='new-blog-post.md'  # Example of output customization
)