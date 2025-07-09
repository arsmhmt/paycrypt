# Make config directory a package
# Re-export the important variables from config.py
from .config import (
    Config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    config,
    JWT_CONFIG
)

__all__ = [
    'Config',
    'DevelopmentConfig',
    'TestingConfig',
    'ProductionConfig',
    'config',
    'JWT_CONFIG'
]
