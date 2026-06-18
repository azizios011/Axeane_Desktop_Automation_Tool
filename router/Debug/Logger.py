# Debug/Logger.py
import sys
from datetime import datetime

class ColorLogger:
    COLORS = {
        'INFO': '\033[94m',     # Blue
        'SUCCESS': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'DEBUG': '\033[95m',    # Purple
        'ENDC': '\033[0m'       # Reset
    }

    @staticmethod
    def _log(level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = ColorLogger.COLORS.get(level, ColorLogger.COLORS['ENDC'])
        print(f"{color}[{timestamp}] [{level}] {message}{ColorLogger.COLORS['ENDC']}")

    @classmethod
    def info(cls, msg): cls._log('INFO', msg)
    @classmethod
    def success(cls, msg): cls._log('SUCCESS', msg)
    @classmethod
    def warn(cls, msg): cls._log('WARNING', msg)
    @classmethod
    def error(cls, msg): cls._log('ERROR', msg)
    @classmethod
    def debug(cls, msg): cls._log('DEBUG', msg)
    