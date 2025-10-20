from crewai import Crew,Process
from Agent import validation_agent, Reportmaker_agent
from tasks import search_task, report_task


# Forming the tech-focused crew with some enhanced configurations
crew = Crew(
  agents=[validation_agent, Reportmaker_agent],
  tasks=[search_task, report_task],
  process=Process.sequential,  # Optional: Sequential task execution is default
  memory=True,
  cache=True,
  max_rpm=100,
  share_crew=True
)

## start the task execution process with enhanced feedback
result=crew.kickoff(inputs={'name':'aditya'})
print(result)