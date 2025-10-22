"""
Main Execution Script
Healthcare Provider Validation System
"""
import sys
from datetime import datetime

from crew import provider_validation_crew
from config import Config
from utils import get_logger

logger = get_logger(__name__)


def validate_provider(provider_name: str, state: str) -> dict:
    """
    Validate a healthcare provider.
    
    Args:
        provider_name: Full name of the provider
        state: Two-letter state code
        
    Returns:
        Dictionary with validation results
    """
    logger.info(f"Starting validation for: {provider_name} ({state})")
    print(f"\n{'='*70}")
    print(f"HEALTHCARE PROVIDER VALIDATION")
    print(f"{'='*70}")
    print(f"Provider: {provider_name}")
    print(f"State: {state}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    try:
        # Execute the crew
        result = provider_validation_crew.kickoff(inputs={
            'provider_name': provider_name,
            'state': state
        })
        
        print(f"\n{'='*70}")
        print(f"VALIDATION COMPLETED SUCCESSFULLY")
        print(f"{'='*70}")
        print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Display the generated report
        report_path = Config.REPORTS_DIR / "provider_validation_report.md"
        if report_path.exists():
            print(f"\n{'='*70}")
            print(f"GENERATED REPORT")
            print(f"{'='*70}")
            print(f"Location: {report_path}")
            print(f"{'='*70}\n")
            
            with open(report_path, 'r', encoding='utf-8') as f:
                print(f.read())
        else:
            logger.warning(f"Report file not found at {report_path}")
            print(f"\n⚠️  Warning: Report file not generated at expected location")
        
        return {
            'status': 'success',
            'result': result,
            'report_path': str(report_path)
        }
    
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        print("\n\n⚠️  Validation interrupted by user")
        return {'status': 'interrupted'}
    
    except Exception as e:
        logger.exception(f"Error during validation: {str(e)}")
        print(f"\n\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }


def main():
    """Main entry point."""
    print(f"\n{'='*70}")
    print(f"HEALTHCARE PROVIDER VALIDATION SYSTEM")
    print(f"Powered by CrewAI Multi-Agent Framework")
    print(f"{'='*70}\n")
    
    # Example usage - modify as needed
    if len(sys.argv) >= 3:
        provider_name = sys.argv[1]
        state = sys.argv[2]
    else:
        # Default example
        provider_name = "John Doe"
        state = "CA"
        print(f"Usage: python main.py \"Provider Name\" STATE")
        print(f"Using default example: {provider_name} in {state}\n")
    
    result = validate_provider(provider_name, state)
    
    # Exit with appropriate code
    if result['status'] == 'success':
        sys.exit(0)
    elif result['status'] == 'interrupted':
        sys.exit(130)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
