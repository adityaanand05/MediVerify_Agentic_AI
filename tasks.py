"""
Task Definitions
Defines all tasks for the healthcare provider validation workflow.
"""

from crewai import Task
from config import Config
from agents import (
    validation_agent,
    enrichment_agent,
    quality_assurance_agent,
    report_maker_agent
)
from utils import get_logger

logger = get_logger(__name__)

# Ensure reports directory exists
Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Task 1: Provider Validation
validation_task = Task(
    description=(
        "Validate healthcare provider: {provider_name} in state: {state}.\n\n"
        "If the provider cannot be found in any verification system, respond only with:\n"
        "'NO_USER_FOUND'\n\n"
        "Otherwise perform verification steps:\n"
        "1. Search NPI Registry\n"
        "2. If pharmacist, validate NABP\n"
        "3. Verify credentials through Propelus ONLY IF a valid license number exists and is at least 3 characters long.\n"
        "   If license number is missing or shorter than 3 characters, skip Propelus verification and continue.\n"
        "4. Cross-reference all sources\n"
        "5. Document discrepancies and results\n\n"
        "IMPORTANT: Never attempt to call Propelus with an empty or invalid license number. Instead state:\n"
        "'Propelus verification skipped: No valid license number available.'"
    ),
    expected_output=(
        "Structured validation report OR 'NO_USER_FOUND'"
    ),
    agent=validation_agent
)

# Task 2: Data Enrichment
enrichment_task = Task(
    description=(
        "Review validation findings for provider: {provider_name}.\n"
        "If result was NO_USER_FOUND, return NO_USER_FOUND.\n"
        "Otherwise perform enrichment:\n"
        "1. Assess completeness\n"
        "2. Identify missing info\n"
        "3. Flag inconsistencies\n"
    ),
    expected_output="Enrichment results OR NO_USER_FOUND",
    agent=enrichment_agent,
    context=[validation_task]
)

# Task 3: Quality Assurance Review
qa_task = Task(
    description=(
        "Conduct quality assurance review.\n"
        "If earlier result equals NO_USER_FOUND, return NO_USER_FOUND.\n"
    ),
    expected_output="QA report OR NO_USER_FOUND",
    agent=quality_assurance_agent,
    context=[validation_task, enrichment_task]
)

# Task 4: Report Generation
report_task = Task(
    description=(
        "Generate final provider validation report.\n"
        "If the input context contains NO_USER_FOUND, return NO_USER_FOUND and do not generate report.\n"
        "If Propelus verification was skipped due to missing license number, mark it clearly in the report.\n"
        "Include sections for:\n"
        "1. Provider Information\n"
        "2. Overall Validation Status\n"
        "3. Detailed Validation Findings\n"
        "4. Compliance Status\n"
        "5. Recommendations & Required Actions\n"
    ),
    expected_output="Markdown report output OR NO_USER_FOUND",
    agent=report_maker_agent,
    context=[validation_task, enrichment_task, qa_task],
    output_file=str(Config.REPORTS_DIR / "provider_validation_report.md")
)

logger.info("All tasks defined successfully")
