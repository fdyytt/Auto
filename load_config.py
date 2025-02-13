import logging
import configparser

logger = logging.getLogger(__name__)

def load_config(filename):
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        return config
    except FileNotFoundError:
        logger.error("Config file not found")
        return None
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return None

filename = 'config.txt'
config = load_config(filename)

if config:
    logger.info("Configuration loaded successfully:")
    for section in config.sections():
        for key, value in config.items(section):
            logger.info(f"{section}.{key} = {value}")