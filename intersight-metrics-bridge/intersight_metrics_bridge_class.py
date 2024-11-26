"""This module defines IntersightMetricsBridge class and methods to poll power data from Cisco UCS servers (Intersight)."""

#!/usr/bin/env python3

import sys
import threading
import yaml

from base_logger import logger

from intersight_client_class import IntersightClient

##############################################################################
#                           IntersightMetricsBridge class                            #
##############################################################################


class IntersightMetricsBridge:
    """
    IntersightMetricsBridge class defines methods to tie together InfluxDBClient, IntersightClient in order to poll power data from various Cisco UCS servers and write it to InfluxDB database.
    """

    def __init__(self):
        logger.info("Initializating IntersightMetricsBridge instance.\n")

        self.influxdb_client = None

        self.list_of_intersight_clients = []

        self.list_of_intersight_servers_to_poll = None

        logger.info("IntersightMetricsBridge instance was successfully initialized.\n")

    def add_intersight_client_to_list_of_intersight_clients(self, intersight_client):
        """This method adds an IntersightClient to the list of Intersight clients assigned to IntersightMetricsBridge.

        Args:
        - intersight_client (instance of class IntersightClient).
        """

        logger.info(
            "Adding IntersightClient %s of Intersight URL %s to IntersightMetricsBridge list of Intersight clients %s.\n",
            intersight_client,
            intersight_client.intersight_url,
            self.list_of_intersight_clients,
        )

        self.list_of_intersight_clients.append(intersight_client)

        logger.info(
            "IntersightClient %s of Intersight URL %s was successfully added to IntersightMetricsBridge list of Intersight clients %s.\n",
            intersight_client,
            intersight_client.intersight_url,
            self.list_of_intersight_clients,
        )

    def assign_clients_and_list_of_servers_to_poll(
        self, servers_inventory_yaml_file_path, request_all_servers=False
    ):
        """This method assigns Intersight clients and Cisco UCS servers to IntersightMetricsBridge instance. The Cisco UCS servers will be monitored for power usage.

        Args:
            - servers_inventory_yaml_file (string) : path to a YAML file describing the inventory of Cisco UCS servers to monitor.
        """

        logger.info(
            "Assigning clients and Cisco UCS servers to IntersightMetricsBridge instance. The Cisco UCS servers will be monitored for power usage.\n"
        )

        try:
            logger.info(
                "YAML inventory file of Cisco UCS servers is at path %s.\n",
                servers_inventory_yaml_file_path,
            )
            with open(
                servers_inventory_yaml_file_path, "r", encoding="utf-8"
            ) as servers_inventory_yaml_file:
                data = yaml.safe_load(servers_inventory_yaml_file)

        except Exception as exception:
            logger.error(
                "Exception of type %s when trying to open YAML file at path %s:\n%s\n",
                exception.__class__.__name__,
                servers_inventory_yaml_file_path,
                exception,
            )

            sys.exit(1)

        if data is not None:
            # Get all Intersight accounts from the data of YAML file and assign list of Intersight clients.
            intersight_domains = data.get("ucs_servers", {}).get(
                "intersight_domains", []
            )

            if intersight_domains == []:
                logger.info("There are no Intersight Domains to monitor.\n")

            for intersight_domain in intersight_domains:
                intersight_domain_ip = intersight_domain.get("intersight_domain_ip", "")
                intersight_key_id = intersight_domain.get("intersight_key_id", "")
                intersight_secret_key_path = intersight_domain.get(
                    "intersight_secret_key_path", ""
                )
                intersight_servers = intersight_domain.get("intersight_servers", [])

                if not intersight_servers:
                    request_all_servers = True

                intersight_client = IntersightClient(
                    intersight_key_id=intersight_key_id,
                    intersight_secret_key_path=intersight_secret_key_path,
                    intersight_url=intersight_domain_ip,
                )

                intersight_client.generate_and_assign_intersight_api_client()

                if request_all_servers:
                    intersight_servers = (
                        intersight_client.get_all_servers_serial_number()
                    )

                intersight_client.assign_list_of_servers_to_monitor(
                    list_of_intersight_servers_to_monitor=intersight_servers
                )

                self.add_intersight_client_to_list_of_intersight_clients(
                    intersight_client=intersight_client
                )
        else:
            logger.warning("There are no Cisco Intersight domains to monitor.\n")

    def assign_influxdb_client(self, influxdb_client):
        """This method assigns an InfluxDBClient to IntersightMetricsBridge.

        Args:
        - influxdb_client (instance of class InfluxDbClient).
        """

        logger.info(
            "Assigning InfluxDbClient %s to IntersightMetricsBridge instance.\n",
            influxdb_client,
        )

        self.influxdb_client = influxdb_client

        logger.info(
            "InfluxDbClient %s instance was successfully assigned to IntersightMetricsBridge instance.\n",
            influxdb_client,
        )

    def assign_intersight_client(self, intersight_client):
        """This method assigns an IntersightClient to IntersightMetricsBridge.

        Args:
        - intersight_client (instance of class IntersightClient).
        """

        logger.info(
            "Assigning IntersightClient %s to IntersightMetricsBridge instance.\n",
            intersight_client,
        )

        self.intersight_client = intersight_client

        logger.info(
            "IntersightClient %s instance was successfully assigned to IntersightMetricsBridge instance.\n",
            intersight_client,
        )

    def start_polling(self, time_interval):
        """This method starts the polling of Cisco UCS servers, managed by Cisco Intersight.
        The start_polling() method of IntersightClient require a list of servers to poll, an InfluxDbClient instance to write data and an interval?

        Args:
        - time_interval (int): number of seconds between the pollings.
        """

        for intersight_client in self.list_of_intersight_clients:
            intersight_client_thread = threading.Thread(
                target=intersight_client.start_polling,
                args=(
                    self.influxdb_client,
                    time_interval,
                ),
            )

            intersight_client_thread.start()
