"""This module is the main module to poll the power usage of Cisco UCS servers."""
#!/usr/bin/env python3

import os
import time

from dotenv import load_dotenv
from base_logger import logger

from influxdb_client_class import InfluxDbClient
from intersight_metrics_bridge_class import IntersightMetricsBridge


##############################################################################
#                               Variables                                    #
##############################################################################

load_dotenv()

# InfluxDB
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")
INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_ORGANIZATION = os.getenv("INFLUXDB_ORGANIZATION")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")

# Servers Inventory File Path
SERVERS_INVENTORY_FILE_PATH = os.getenv("INTERSIGHT_METRICS_BRIDGE_CONFIG_INVENTORY")

##############################################################################
#                                  Main                                      #
##############################################################################

if __name__ == "__main__":
    # Wait for containers init
    time.sleep(10)

    # Create a IntersightMetricsBridge instance.
    new_intersight_metrics_bridge = IntersightMetricsBridge()

    # Assign InfluxDbClient instance to IntersightMetricsBridge instance.
    new_intersight_metrics_bridge.assign_influxdb_client(
        influxdb_client=InfluxDbClient(
            bucket=INFLUXDB_BUCKET, influxdb_url=INFLUXDB_URL, org=INFLUXDB_ORGANIZATION, token=INFLUXDB_TOKEN
        )
    )
    # Assign a list of Intersight clients and servers to IntersightMetricsBridge instance for power usage monitoring.
    new_intersight_metrics_bridge.assign_clients_and_list_of_servers_to_poll(
        servers_inventory_yaml_file_path=SERVERS_INVENTORY_FILE_PATH
    )

    # Start IntersightMetricsBridge polling.
    new_intersight_metrics_bridge.start_polling(time_interval=60)
