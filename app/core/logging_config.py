import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )


logger = logging.getLogger("moinsystems_ai")
