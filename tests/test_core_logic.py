import pytest
import logging
from src.core.logger import setup_logger
import os

def test_setup_logger():
    # Test logger initialization
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"

    # Test logging to file (optional check if it exists)
    logger.info("Test message")

def test_logger_levels():
    logger = setup_logger("multi_level", level="DEBUG")
    logger.debug("Debug")
    logger.error("Error")
    assert logger.level == logging.DEBUG
