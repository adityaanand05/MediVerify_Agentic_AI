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
        "Execute the following verification steps:\n"
        "1. Search NPI Registry for provider's NPI number, specialty, and practice address\n"
        "2. If pharmacist, validate license through NABP e-Profile system\n"
        "3. Verify credentials through Propelus Primary Source Verification\n"
        "4. Cross-reference data across all three sources\n"
        "5. Identify and document any discrepancies\n\n"
        "For each source, document:\n"
        "- Verification status (verified/not found/error)\n"
        "- Key data points obtained (NPI, license number, specialty, address)\n"
        "- Any warnings or concerns\n"
        "- Data quality assessment"
    ),
    expected_output=(
        "Structured validation report containing:\n"
        "- Provider identification (name, NPI, license numbers)\n"
        "- Verification status from each source (NPI, NABP, Propelus)\n"
        "- Complete address and contact information\n"
        "- Specialty/taxonomy information\n"
        "- License status and expiration dates\n"
        "- Any discrepancies or concerns identified\n"
        "- Data quality score (high/medium/low)"
    ),
    agent=validation_agent
)

# Task 2: Data Enrichment
enrichment_task = Task(
    description=(
        "Review the validation findings for provider: {provider_name}.\n\n"
        "Perform data quality analysis:\n"
        "1. Assess completeness of gathered data\n"
        "2. Identify any missing critical information\n"
        "3. Flag inconsistencies between sources\n"
        "4. Determine if additional verification is needed\n"
        "5. Provide recommendations for data improvement\n\n"
        "Focus areas:\n"
        "- Address consistency across sources\n"
        "- License expiration status\n"
        "- Specialty/taxonomy alignment\n"
        "- Contact information completeness\n"
        "- Any regulatory concerns"
    ),
    expected_output=(
        "Data enrichment analysis containing:\n"
        "- Completeness assessment (% of critical fields populated)\n"
        "- List of missing or incomplete data elements\n"
        "- Identified discrepancies with severity ratings\n"
        "- Recommendations for additional verification\n"
        "- Enhanced data quality score with justification"
    ),
    agent=enrichment_agent,
    context=[validation_task]
)

# Task 3: Quality Assurance Review
qa_task = Task(
    description=(
        "Conduct final quality assurance review for provider: {provider_name}.\n\n"
        "Quality checks to perform:\n"
        "1. Verify all required data elements are present\n"
        "2. Confirm consistency across all sources\n"
        "3. Validate that licenses are current and active\n"
        "4. Check for any disciplinary actions or sanctions\n"
        "5. Ensure compliance with credentialing standards\n"
        "6. Assess overall data reliability\n\n"
        "Compliance standards:\n"
        "- CMS Medicare provider directory requirements\n"
        "- NCQA credentialing standards\n"
        "- State-specific licensing requirements\n"
        "- Organizational credentialing policies"
    ),
    expected_output=(
        "Quality assurance report containing:\n"
        "- Overall quality assessment (Pass/Pass with concerns/Fail)\n"
        "- Compliance checklist with pass/fail for each requirement\n"
        "- Critical issues requiring immediate attention\n"
        "- Non-critical issues for future follow-up\n"
        "- Final recommendation (Approve/Request additional info/Deny)\n"
        "- QA reviewer notes and observations"
    ),
    agent=quality_assurance_agent,
    context=[validation_task, enrichment_task]
)

# Task 4: Report Generation
report_task = Task(
    description=(
        "Generate comprehensive provider validation report for: {provider_name}.\n\n"
        "Report structure:\n"
        "1. Executive Summary\n"
        "   - Provider overview\n"
        "   - Validation status\n"
        "   - Key findings\n"
        "   - Recommendation\n\n"
        "2. Provider Information\n"
        "   - Demographics\n"
        "   - NPI and license numbers\n"
        "   - Practice location(s)\n"
        "   - Specialty information\n\n"
        "3. Verification Results\n"
        "   - NPI Registry findings\n"
        "   - NABP validation results (if applicable)\n"
        "   - Propelus verification status\n\n"
        "4. Data Quality Assessment\n"
        "   - Completeness score\n"
        "   - Consistency analysis\n"
        "   - Identified gaps\n\n"
        "5. Quality Assurance Review\n"
        "   - Compliance status\n"
        "   - Issues and concerns\n"
        "   - Recommendations\n\n"
        "6. Appendices\n"
        "   - Detailed source data\n"
        "   - Verification timestamps\n"
        "   - Reviewer information\n\n"
        "Format: Professional Markdown document"
    ),
    expected_output=(
        "Complete provider validation report in Markdown format saved to disk. "
        "Report must be professional, comprehensive, and suitable for credentialing "
        "committee review. All sections must be clearly organized with appropriate "
        "headers, and findings must be presented with supporting evidence from "
        "verification sources."
    ),
    agent=report_maker_agent,
    context=[validation_task, enrichment_task, qa_task],
    output_file=str(Config.REPORTS_DIR / "provider_validation_report.md")
)

logger.info("All tasks defined successfully")
