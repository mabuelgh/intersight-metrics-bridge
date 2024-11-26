"""This module defines logging format."""

#!/usr/bin/env python3

import logging

FORMAT = "%(asctime)-15s [%(levelname)s] [%(filename)s:%(lineno)s %(threadName)s %(funcName)s()] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
logger = logging.getLogger("intersight_metrics_bridge")
