from crewai import Crew, Process
from Agent import validation_agent, Reportmaker_agent
from tasks import search_task, report_task


crew = Crew(
    agents=[validation_agent, Reportmaker_agent],
    tasks=[search_task, report_task],
    process=Process.sequential,
    max_rpm=100,
    share_crew=True
)


result = crew.kickoff(inputs={'name': 'aditya sharma', 'state': 'CA'})
print(result)