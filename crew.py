"""
Crew Configuration
Main crew orchestration for healthcare provider validation.
"""
from crewai import Crew, Process

from config import Config
from agents import (
    validation_agent,
    enrichment_agent,
    quality_assurance_agent,
    report_maker_agent
)
from tasks import validation_task, enrichment_task, qa_task, report_task
from utils import get_logger

logger = get_logger(__name__)

# Create the crew
provider_validation_crew = Crew(
    agents=[
        validation_agent,
        enrichment_agent,
        quality_assurance_agent,
        report_maker_agent
    ],
    tasks=[
        validation_task,
        enrichment_task,
        qa_task,
        report_task
    ],
    process=Process.sequential,
    max_rpm=Config.CREW_MAX_RPM,
    verbose=True,
    share_crew=True
)

logger.info("Provider validation crew configured successfully")
