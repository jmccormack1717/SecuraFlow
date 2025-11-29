"""Logging configuration."""
import logging
import sys
import json
from app.config import settings

def get_logger(name: str) -> logging.Logger:
    """Get configured logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        # Use JSON formatter if structured logging is enabled
        if getattr(settings, 'structured_logging', False):
            formatter = logging.Formatter('%(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

