import logging
import os


def make_logger(name, level=logging.INFO, filepath=None):
    if isinstance(level, str):
        try:
            level = getattr(logging, level.upper())
        except AttributeError:
            level = logging.INFO

    logger = logging.Logger(name)

    f = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )

    h = logging.StreamHandler()
    h.setLevel(level)
    h.setFormatter(f)
    logger.addHandler(h)

    if filepath and os.path.isdir(os.path.dirname(filepath)):
        h = logging.FileHandler(filename=filepath, encoding='utf-8')
        h.setLevel(level)
        h.setFormatter(f)
        logger.addHandler(h)

    return logger
