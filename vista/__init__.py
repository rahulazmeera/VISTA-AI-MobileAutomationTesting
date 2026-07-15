"""VISTA — Vision-based Intelligent Screen Test Automation."""

__version__ = "0.1.0"
__author__ = "VISTA Contributors"
__license__ = "Apache-2.0"

from vista.dsl.steps import Step
from vista.driver.base import Driver
from vista.runner.engine import Runner
from vista.vision.screen import ScreenState

__all__ = ["Step", "Driver", "ScreenState", "Runner", "__version__"]
