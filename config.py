"""
Configuration Management Module
Loads and validates all environment variables and application settings.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables
load_dotenv()



class Config:
    """Application configuration loaded from environment variables."""
    
    # Gemini API Configuration (Primary)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-2.5-flash-exp")
    GEMINI_TEMPERATURE = float(os.getenv("GEMINI_TEMPERATURE", "0.1"))
    
    # Propelus API Configuration
    PROPELUS_API_KEY = os.getenv("PROPELUS_API_KEY")
    PROPELUS_BASE_URL = os.getenv("PROPELUS_BASE_URL", "https://api.propelus.com/v1/license/verify")
    
    # NABP API Configuration
    NABP_API_KEY = os.getenv("NABP_API_KEY")
    NABP_BASE_URL = os.getenv("NABP_BASE_URL", "https://api.nabp.pharmacy/v2/Individual/eprofile/validate")
    
    # NPI Registry Configuration
    NPI_BASE_URL = "https://npiregistry.cms.hhs.gov/api/"
    
    # CrewAI Configuration
    AGENT_MAX_RPM = int(os.getenv("AGENT_MAX_RPM", "10"))
    CREW_MAX_RPM = int(os.getenv("CREW_MAX_RPM", "50"))
    
    # Application Settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
    RETRY_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "0.3"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Reports Directory
    REPORTS_DIR = Path(os.getenv("REPORTS_DIR", "./reports"))
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        required_vars = {
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
        }
        
        # Optional but recommended
        optional_vars = {
            "PROPELUS_API_KEY": cls.PROPELUS_API_KEY,
            "NABP_API_KEY": cls.NABP_API_KEY,
        }
        
        missing = [name for name, value in required_vars.items() if not value]
        
        if missing:
            print("❌ ERROR: Missing required environment variables:")
            for var in missing:
                print(f"   - {var}")
            print("\nPlease create a .env file with your API keys")
            sys.exit(1)
        
        # Warn about missing optional keys
        missing_optional = [name for name, value in optional_vars.items() if not value]
        if missing_optional:
            print("⚠️  WARNING: Missing optional API keys:")
            for var in missing_optional:
                print(f"   - {var}")
            print("   Some features may not work without these keys\n")
        
        # Create reports directory if it doesn't exist
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        return True
    
    @classmethod
    def display_config(cls):
        """Display current configuration (without sensitive data)."""
        print("="*70)
        print("CONFIGURATION")
        print("="*70)
        print(f"Gemini Model: {cls.GEMINI_MODEL}")
        print(f"Temperature: {cls.GEMINI_TEMPERATURE}")
        print(f"Agent Max RPM: {cls.AGENT_MAX_RPM}")
        print(f"Crew Max RPM: {cls.CREW_MAX_RPM}")
        print(f"Max Retries: {cls.MAX_RETRIES}")
        print(f"API Timeout: {cls.API_TIMEOUT}s")
        print(f"Reports Dir: {cls.REPORTS_DIR}")
        print(f"Gemini API Key: {'✓ Set' if cls.GEMINI_API_KEY else '✗ Missing'}")
        print(f"Propelus API Key: {'✓ Set' if cls.PROPELUS_API_KEY else '✗ Missing'}")
        print(f"NABP API Key: {'✓ Set' if cls.NABP_API_KEY else '✗ Missing'}")
        print("="*70)



# Validate configuration on import
Config.validate()
