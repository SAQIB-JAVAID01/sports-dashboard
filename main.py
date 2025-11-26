"""
Main Application Entry Point
Sports Forecasting Platform - Desktop Application
Supports both GUI (PyQt6) and headless modes
"""

import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
import logging
from pathlib import Path
import pandas as pd
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("main")

# Import application components
from src.utils.activation import ActivationManager, LicenseManager
from src.api_client import SportsAPIClient
from src.prediction import PredictionService

# Try to import GUI components (optional)
try:
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from src.gui.main_window import MainWindow
    GUI_AVAILABLE = True
except ImportError as e:
    logger.warning(f"PyQt6 GUI not available: {e}")
    GUI_AVAILABLE = False
    QApplication = None
    MainWindow = None


# Import all CSVs from your first main folder
folder1 = r"C:\Users\Admin\New Recordings\udemy\Data Analyst Bootcamp\Python\1-python basics\Sports-Project-mainRev8\Sports-Project-main\LL9_4_DOMAIN_AWARE_MODELS_AND_WEIGHTS_WITH_SHAP"
csv_files = glob.glob(os.path.join(folder1, "*.csv"))
dataframes = [pd.read_csv(f) for f in csv_files]
all_data = pd.concat(dataframes, ignore_index=True)
print("Imported data shape:", all_data.shape)
print(all_data.head())


def main_cli():
    """Run application in headless/CLI mode"""
    
    logger.info("=" * 60)
    logger.info("Sports Forecasting Platform - CLI Mode")
    logger.info("=" * 60)
    
    try:
        # Initialize services
        logger.info("Initializing services...")
        
        activation_manager = ActivationManager()
        api_client = SportsAPIClient()
        prediction_service = PredictionService()
        
        # Load models
        if prediction_service.load_models():
            logger.info(" Prediction models loaded successfully")
        else:
            logger.warning(" Prediction models not available (will use fallback logic)")
        
        # Check activation
        is_active, message = activation_manager.check_activation()
        logger.info(f"License Status: {message}")
        
        # Show status
        print("\n" + "=" * 60)
        print("SPORTS FORECASTING PLATFORM - CLI MODE")
        print("=" * 60)
        print(f"\nLicense: {message}")
        print(f"API Client: READY")
        print(f"Models: {'LOADED' if prediction_service.models_loaded else 'READY'}")
        print(f"Sports: {', '.join(api_client.get_sports())}")
        
        print("\nAvailable Commands:")
        print("  python main.py --help")
        print("  python test_validation.py (run diagnostics)")
        print("  python generate_key.py (generate license)")
        
        print("\nTo launch GUI (requires PyQt6):")
        print("  pip install PyQt6")
        print("  python main.py --gui")
        
        print("\n" + "=" * 60 + "\n")
        
        return 0
        
    except Exception as e:
        logger.error(f" Critical error: {e}", exc_info=True)
        print(f"\n ERROR: {e}\n")
        return 1


def main_gui():
    """Run application in GUI mode"""
    
    if not GUI_AVAILABLE:
        logger.error("PyQt6 not available - falling back to CLI mode")
        print("\n PyQt6 GUI framework not available")
        print("\nTo use GUI mode, install PyQt6:")
        print("  pip install PyQt6")
        print("\nRunning in CLI mode instead...\n")
        return main_cli()
    
    logger.info("=" * 60)
    logger.info("Sports Forecasting Platform - GUI Mode")
    logger.info("=" * 60)
    
    try:
        # Initialize PyQt application
        app = QApplication(sys.argv)
        app.setApplicationName("Sports Forecasting Platform")
        app.setApplicationVersion("1.0.0")
        
        logger.info(" PyQt6 application initialized")
        
        # Initialize core services
        logger.info("Initializing services...")
        
        activation_manager = ActivationManager()
        api_client = SportsAPIClient()
        prediction_service = PredictionService()
        
        # Load models
        if prediction_service.load_models():
            logger.info(" Prediction models loaded successfully")
        else:
            logger.warning(" Prediction models not available (will use fallback logic)")
        
        # Create main window
        logger.info("Creating main window...")
        main_window = MainWindow(activation_manager, api_client, prediction_service)
        
        # Check activation status
        is_active, message = activation_manager.check_activation()
        if is_active:
            logger.info(f" {message}")
            main_window.add_log(f" Application Activated - {message}")
        else:
            logger.warning(f" {message}")
            main_window.add_log(f" {message}")
            QMessageBox.warning(
                main_window,
                "License Required",
                f"{message}\n\n"
                "Please activate the application using File > Activate License\n"
                "or the Activate button in the toolbar."
            )
        
        # Show main window
        main_window.show()
        logger.info(" Main window displayed")
        logger.info("=" * 60)
        logger.info("Application started successfully")
        logger.info("=" * 60)
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f" Critical error: {e}", exc_info=True)
        print(f"\n CRITICAL ERROR:\n{e}\n")
        print("Please check app.log for details")
        sys.exit(1)


def main():
    """Main application entry point"""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--help', '-h']:
            print("""
Sports Forecasting Platform v1.0.0

Usage: python main.py [OPTIONS]

Options:
  --gui          Launch GUI application (default if PyQt6 available)
  --cli          Launch in headless CLI mode
  --help, -h     Show this help message

Examples:
  python main.py              # Auto-detect (GUI if available, else CLI)
  python main.py --gui        # Force GUI mode
  python main.py --cli        # Force CLI mode
  python main.py --help       # Show this message

Other utilities:
  python test_validation.py   # Run system diagnostics
  python generate_key.py      # Generate/validate license keys
  python STATUS.py            # Show platform status
            """)
            return 0
        
        elif arg in ['--gui']:
            return main_gui() if GUI_AVAILABLE else main_cli()
        
        elif arg in ['--cli']:
            return main_cli()
    
    # Auto-detect mode
    if GUI_AVAILABLE:
        logger.info("PyQt6 detected - launching GUI mode")
        return main_gui()
    else:
        logger.info("PyQt6 not available - launching CLI mode")
        return main_cli()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code if exit_code is not None else 0)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n Error: {e}\n")
        sys.exit(1)
