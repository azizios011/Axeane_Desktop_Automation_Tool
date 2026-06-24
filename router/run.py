# run.py
import sys
import os
import argparse
import logging
from pathlib import Path

def setup_logging(verbose=False):
    """Configure logging for the application"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['playwright', 'httpx', 'pdfplumber']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Please install them with: pip install " + " ".join(missing))
        sys.exit(1)

def main():
    """Main entry point for running the application"""
    parser = argparse.ArgumentParser(
        description='Axeane Kompta Automation Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Launch with default settings
  python run.py --verbose          # Launch with detailed logging
  python run.py --headless         # Run browser in headless mode
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (no visible window)'
    )
    
    parser.add_argument(
        '--debug-network',
        action='store_true',
        help='Enable network request/response logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting Axeane Kompta Automation Engine...")
    
    # Check dependencies
    check_dependencies()
    
    # Set environment variables based on arguments
    if args.headless:
        os.environ['AXEANE_HEADLESS'] = '1'
        logger.info("Running in headless mode")
    
    if args.debug_network:
        os.environ['AXEANE_DEBUG_NETWORK'] = '1'
        logger.info("Network debugging enabled")
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    try:
        # Import and run main
        import main
        logger.info("✅ Application started successfully")
        main.main()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
