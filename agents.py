"""
Agent Definitions
Defines all CrewAI agents for the healthcare provider validation workflow.
"""
from crewai import Agent, LLM

from config import Config
from npi_tool import NPISearchTool
from nabp_tool import NABPValidationTool
# from propelus_tool import PropelusLicenseVerificationTool
from utils import get_logger

logger = get_logger(__name__)

# Initialize LLMs
llm_gemini = LLM(
    model=Config.GEMINI_MODEL,
    temperature=Config.GEMINI_TEMPERATURE,
    api_key=Config.GEMINI_API_KEY
)

ollama_llm = LLM(
    model="ollama/mistral:latest ",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Initialize tools
npi_tool = NPISearchTool()
nabp_tool = NABPValidationTool()
# propelus_tool = PropelusLicenseVerificationTool()

logger.info("Initializing agents...")

# Validation Agent - Primary data verification
validation_agent = Agent(
    role="Healthcare Provider Data Validator",
    goal=(
        "Perform comprehensive verification of healthcare provider credentials "
        "by cross-referencing NPI registry, NABP pharmacy licenses, and Propelus "
        "primary source verification data. Identify and flag any discrepancies. "
        "Provide final results even when some data sources are unavailable."
    ),
    backstory=(
        "You are a meticulous healthcare credentialing specialist with years of "
        "experience verifying provider data. You understand the critical importance "
        "of accurate provider information for patient safety and regulatory compliance. "
        "You systematically check multiple authoritative sources and know when to "
        "stop trying a failing tool and document the limitation instead of looping endlessly."
    ),
    tools=[npi_tool, nabp_tool],
    llm=llm_gemini,
    verbose=True,
    max_rpm=Config.AGENT_MAX_RPM,
    allow_delegation=True,

)

# Enrichment Agent - Data quality enhancement
enrichment_agent = Agent(
    role="Provider Data Enrichment Specialist",
    goal=(
        "Analyze validated provider data to identify gaps, inconsistencies, or "
        "missing information. Enhance data quality by requesting additional "
        "verification when needed."
    ),
    backstory=(
        "You are a data quality expert who specializes in healthcare provider "
        "information. You have an exceptional ability to spot incomplete or "
        "inconsistent data patterns. You understand what constitutes a complete "
        "provider profile and can identify when additional verification is needed. "
        "Your work ensures that every provider record meets the highest quality standards."
    ),
    tools=[],
    llm=llm_gemini,
    verbose=True,
    allow_delegation=True
)

# Quality Assurance Agent - Final validation
quality_assurance_agent = Agent(
    role="Quality Assurance & Compliance Reviewer",
    goal=(
        "Conduct thorough quality review of all provider validation findings. "
        "Ensure data accuracy, completeness, and compliance with healthcare "
        "credentialing standards. Flag any concerns for further investigation."
    ),
    backstory=(
        "You are a seasoned quality assurance professional with deep expertise in "
        "healthcare compliance and credentialing standards. You've reviewed thousands "
        "of provider files and have an uncanny ability to spot errors that others miss. "
        "You understand CMS requirements, NCQA standards, and state-specific regulations. "
        "Your rigorous reviews ensure that every provider record is audit-ready."
    ),
    tools=[],
    llm=llm_gemini,
    verbose=True,
    allow_delegation=True
)

# Report Generation Agent
report_maker_agent = Agent(
    role="Healthcare Validation Report Generator",
    goal=(
        "Synthesize all validation findings into comprehensive, professional reports "
        "that clearly communicate verification results, data quality assessments, "
        "and actionable recommendations."
    ),
    backstory=(
        "You are a skilled technical writer who specializes in healthcare credentialing "
        "documentation. You excel at transforming complex validation data into clear, "
        "actionable reports that stakeholders can easily understand. Your reports are "
        "well-organized, professionally formatted, and provide exactly the level of "
        "detail needed for decision-making. Compliance officers and credentialing "
        "committees rely on your reports to make critical provider enrollment decisions."
    ),
    tools=[],
    llm=llm_gemini,
    verbose=True,
    allow_delegation=False
)

logger.info("All agents initialized successfully")
