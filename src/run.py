"""
main entry point for the data pipeline application.
"""
from dotenv import load_dotenv
from config import load_config
from shared.telemetry.logging import PythonLogger
from pipeline.pipeline import DataPipeline

load_dotenv()

# Initialize app config and logger
app_config = load_config()
logger = PythonLogger.get_logger(config=app_config)


if __name__ == "__main__":
    # Directory to watch for file events
    directory_to_watch = "src/landed_files/"

    # Initialize the data pipeline
    pipeline = DataPipeline(
        directory=directory_to_watch, logger=logger, config=app_config
    )

    # Run the pipeline
    pipeline.run()
