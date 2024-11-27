"""This module defines IntersightClient class and methods to fetch power data of Cisco UCS servers managed by Cisco Intersight."""

#!/usr/bin/env python3

import datetime
import pprint
import sys
import time
import urllib3

import intersight
from intersight.api import compute_api, telemetry_api
import intersight.model.telemetry_druid_aggregator
import intersight.model.telemetry_druid_and_filter
import intersight.model.telemetry_druid_data_source
import intersight.model.telemetry_druid_expression_post_aggregator
import intersight.model.telemetry_druid_filter
import intersight.model.telemetry_druid_period_granularity
import intersight.model.telemetry_druid_query_context
import intersight.model.telemetry_druid_time_series_request

from base_logger import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##############################################################################
#                          IntersightClient class                            #
##############################################################################


class IntersightClient:
    """
    IntersightClient class defines methods to authenticate and fetch power data of Cisco UCS servers managed by Cisco Intersight.
    """

    def __init__(self, intersight_key_id, intersight_secret_key_path, intersight_url):
        logger.info(
            "Initializating IntersightClient instance with Cisco Intersight at URL %s.\n",
            intersight_url,
        )

        self._intersight_key_id = intersight_key_id
        self._intersight_secret_key_path = intersight_secret_key_path
        self.intersight_url = intersight_url

        self._api_client = None
        self.list_of_intersight_servers_to_monitor = []

        logger.info(
            "IntersightClient instance was successfully initialized with Cisco Intersight at URL %s.\n",
            intersight_url,
        )

    def assign_list_of_servers_to_monitor(self, list_of_intersight_servers_to_monitor):
        """This method assigns a list of Cisco UCS server managed by Cisco Intersight to IntersightClient for power usage monitoring.

        Args:
        - list_of_intersight_servers_to_monitor (list of dictionnaries): list of dictionnaries describing Cisco UCS servers managed by Cisco Intersight.
        It has the following format [{"server":<server_serial_number>},{...}]
        """

        logger.info(
            "Assigning list of Cisco UCS servers %s managed by Intersight %s for power usage monitoring.\n",
            list_of_intersight_servers_to_monitor,
            self.intersight_url,
        )

        self.list_of_intersight_servers_to_monitor = (
            list_of_intersight_servers_to_monitor
        )

        logger.info(
            "List of Cisco UCS servers %s managed by Intersight %s was successfully assigned for power usage monitoring.\n",
            list_of_intersight_servers_to_monitor,
            self.intersight_url,
        )

    def generate_and_assign_intersight_api_client(self):
        """This method generates Intersight ApiClient object with Cisco Intersight API key ID and Cisco Intersight API secret key.
        Then, it assigns ApiClient to IntersightClient "_api_client" attribute.

        Returns:
        - api_client (Intersight ApiClient object): ApiClient is used to authenticate and communicate with Cisco Intersight API.
        """

        logger.info(
            "Generating Intersight API Client for authentication to Intersight.\n"
        )

        # Set signing info for V2 or V3 type of auth
        if "RSA" in open(self._intersight_secret_key_path, encoding="utf-8").read():
            # V2
            signing_scheme = intersight.signing.SCHEME_RSA_SHA256
            signing_algorithm = intersight.signing.ALGORITHM_RSASSA_PKCS1v15
        else:
            # V3
            signing_scheme = intersight.signing.SCHEME_HS2019
            signing_algorithm = intersight.signing.ALGORITHM_ECDSA_MODE_FIPS_186_3

        intersight_key_id = self._intersight_key_id

        configuration = intersight.Configuration(
            host=self.intersight_url,
            signing_info=intersight.signing.HttpSigningConfiguration(
                key_id=intersight_key_id,
                private_key_path=self._intersight_secret_key_path,
                # For OpenAPI v2
                # signing_scheme=intersight.signing.SCHEME_RSA_SHA256,
                # For OpenAPI v3
                # signing_scheme=intersight.signing.SCHEME_HS2019,
                # For OpenAPI v2
                # signing_algorithm=intersight.signing.ALGORITHM_RSASSA_PKCS1v15,
                # For OpenAPI v3
                # signing_algorithm=intersight.signing.ALGORITHM_ECDSA_MODE_FIPS_186_3,
                signing_scheme=signing_scheme,
                signing_algorithm=signing_algorithm,
                signed_headers=[
                    intersight.signing.HEADER_REQUEST_TARGET,
                    intersight.signing.HEADER_CREATED,
                    intersight.signing.HEADER_EXPIRES,
                    intersight.signing.HEADER_HOST,
                    intersight.signing.HEADER_DATE,
                    intersight.signing.HEADER_DIGEST,
                    "Content-Type",
                    "User-Agent",
                ],
                signature_max_validity=datetime.timedelta(minutes=5),
            ),
        )

        configuration.discard_unknown_keys = True
        configuration.disabled_client_side_validations = "minimum"
        configuration.verify_ssl = False
        api_client = intersight.ApiClient(configuration)
        api_client.set_default_header("Content-Type", "application/json")

        self._api_client = api_client

        logger.info(
            "Intersight API Client was successfully generated for authentication to Intersight and assigned to IntersightClient.\n"
        )

    def generate_data_for_influxdb(
        self, intersight_server, current_power_usage_of_intersight_server, timestamp
    ):
        """This method generates data formatted for InfluxDB database.

        Args:
        - intersight_server (string): Cisco UCS server (serial number) managed by Cisco Intersight.
        - current_power_usage_of_intersight_server (float): current power usage of the Cisco UCS server managed by Cisco Intersight.
        - timestamp (string): timestamp of the power usage of the Cisco UCS server managed by Cisco Intersight.

        Returns:
        - power_usage_of_intersight_server_influxdb_data (list of dictionnary): power usage of the Cisco UCS server managed by Cisco Intersight as data formatted for InfluxDB database.
        """
        # Create data for InfluxDB.
        power_usage_of_intersight_server_influxdb_data = [
            {
                "measurement": "power_usage_ucs_servers_intersight",
                "tags": {
                    "server": f"{intersight_server}",
                },
                "fields": {
                    "current_power_usage_of_ucs_server": float(
                        current_power_usage_of_intersight_server
                    )
                },
                "time": timestamp,
            }
        ]

        logger.info(
            "Following data describing power usage of Cisco UCS server %s managed by Intersight for the timestamp %s is ready to be written to InfluxDB database:\n%s\n",
            intersight_server,
            timestamp,
            pprint.pformat(power_usage_of_intersight_server_influxdb_data),
        )

        return power_usage_of_intersight_server_influxdb_data

    def get_power_usage_of_intersight_server(self, intersight_server):
        """This method fetches power usage of Cisco UCS server managed by Cisco Intersight.
        It returns data formatted for InfluxDB database.

        Args:
        - intersight_server (string): Cisco UCS server (serial number) managed by Cisco Intersight.

        Returns:
        - power_usage_of_intersight_server_influxdb_data (list of dictionnary): power usage of the Cisco UCS server managed by Cisco Intersight as data formatted for InfluxDB database.
        """

        logger.info(
            "Fetching power usage of Cisco UCS server %s managed by Intersight.\n",
            intersight_server,
        )

        # Create time period that includes the last minute.
        current_time = datetime.datetime.now()
        end_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-7]
        start_time = (current_time - datetime.timedelta(minutes=1)).strftime(
            "%Y-%m-%dT%H:%M:%S.%f"
        )[:-7]
        period = start_time + "+02:00/" + end_time + "+02:00"

        logger.info(
            "The fetching of power usage of Cisco UCS server %s managed by Intersight is for the period %s.\n",
            intersight_server,
            period,
        )

        # Create an api_instance of TelemetryApi.
        api_instance = telemetry_api.TelemetryApi(self._api_client)

        # Create payload for the API request.
        request_payload = intersight.model.telemetry_druid_time_series_request.TelemetryDruidTimeSeriesRequest(
            aggregations=[
                intersight.model.telemetry_druid_aggregator.TelemetryDruidAggregator(
                    field_name="hw.host.power_count",
                    type="longSum",
                    name="count",
                ),
                intersight.model.telemetry_druid_aggregator.TelemetryDruidAggregator(
                    field_name="hw.host.power",
                    type="doubleSum",
                    name="hw.host.power-Sum",
                ),
                intersight.model.telemetry_druid_aggregator.TelemetryDruidAggregator(
                    field_name="host.id",
                    type="thetaSketch",
                    name="endpoint_count",
                ),
            ],
            data_source=intersight.model.telemetry_druid_data_source.TelemetryDruidDataSource(
                type="table",
                name="PhysicalEntities",
            ),
            dimensions=[],
            filter=intersight.model.telemetry_druid_and_filter.TelemetryDruidAndFilter(
                type="and",
                fields=[
                    intersight.model.telemetry_druid_filter.TelemetryDruidFilter(
                        type="selector",
                        dimension="serial_number",
                        value=f"{intersight_server}",
                    ),
                    intersight.model.telemetry_druid_filter.TelemetryDruidFilter(
                        type="selector",
                        dimension="instrument.name",
                        value="hw.host",
                    ),
                ],
            ),
            granularity=intersight.model.telemetry_druid_period_granularity.TelemetryDruidPeriodGranularity(
                type="period",
                period="PT1M",
                timeZone="Europe/Paris",
            ),
            intervals=[period],
            post_aggregations=[
                intersight.model.telemetry_druid_expression_post_aggregator.TelemetryDruidExpressionPostAggregator(
                    type="expression",
                    name="hw-host-power-Avg",
                    expression='("hw.host.power-Sum" / "count")',
                ),
            ],
            query_type="groupBy",
        )

        try:
            # Perform a Druid TimeSeries API call.
            resp_get_power_usage_of_intersight_server = (
                api_instance.query_telemetry_time_series(
                    telemetry_druid_time_series_request=request_payload
                )
            )

        except intersight.ApiException as exception:
            logger.error(
                "Exception of type %s when calling TelemetryApi->query_telemetry_time_series:\n%s\n",
                exception.__class__.__name__,
                exception,
            )

            sys.exit(1)

        logger.info(
            "Following data describing power usage of Cisco UCS server %s managed by Intersight for the period %s was fetched:\n%s\n",
            intersight_server,
            period,
            pprint.pformat(resp_get_power_usage_of_intersight_server),
        )

        if not resp_get_power_usage_of_intersight_server:
            logger.warning(
                "Current power usage of Cisco UCS server %s managed by Intersight was NOT fetched for the period %s.\n",
                intersight_server,
                period,
            )
            return

        current_power_usage_of_intersight_server = (
            resp_get_power_usage_of_intersight_server[0]
            .get("event", None)
            .get("hw-host-power-Avg", None)
        )

        logger.info(
            "Current power usage of Cisco UCS server %s managed by Intersight for the period %s is %s Watt.\n",
            intersight_server,
            period,
            current_power_usage_of_intersight_server,
        )

        # Get the timestamp of the power usage of the Cisco UCS server managed by Cisco Intersight.
        timestamp = (
            resp_get_power_usage_of_intersight_server[0]
            .get("timestamp", None)
            .isoformat()[:-7]
            + "-01:00/"
        )

        # Create data for InfluxDB.
        power_usage_of_intersight_server_influxdb_data = self.generate_data_for_influxdb(
            intersight_server=intersight_server,
            current_power_usage_of_intersight_server=current_power_usage_of_intersight_server,
            timestamp=timestamp,
        )

        return power_usage_of_intersight_server_influxdb_data

    def get_all_servers_serial_number(self):
        """This method will get all the Serial Numbers from the servers in an Intersight domain.

        Args:
        - intersight_client (intersight_client_class.IntersightClient): client to make API call on Intersight account

        Returns:
        - server_list (list of dictionnaries): list of dictionnaries describing Cisco UCS servers managed by Cisco Intersight.
        """

        logger.info(
            "Fetching the Serial Numbers of all servers in Intersight account: %s\n",
            self.intersight_url,
        )

        api_instance = compute_api.ComputeApi(self._api_client)

        try:
            servers_list_from_api = (
                api_instance.get_compute_physical_summary_list().results
            )
            server_list = []
            for server in servers_list_from_api:
                if server["management_mode"] in ["UCSM", "Intersight"]:
                    server_dict = {"server": server["serial"]}
                    server_list.append(server_dict)

            return server_list

        except intersight.ApiException as exception:
            logger.error(
                "Exception of type %s when calling ComputeApi->get_compute_physical_summary_list:\n%s\n",
                exception.__class__.__name__,
                exception,
            )

            sys.exit(1)

    def start_polling(self, influxdb_client, time_interval):
        """This method starts to poll Cisco UCS servers managed by Cisco Intersight.

        Args:
        - influxdb_client: InfluxDbClient instance.
        - time_interval (int): number of seconds between the pollings.
        """

        logger.info(
            "Starting new Intersight Client thread to poll Cisco UCS servers managed by Intersight.\n"
        )

        while True:

            for intersight_server in self.list_of_intersight_servers_to_monitor:
                power_usage_of_intersight_server_influxdb_data = (
                    self.get_power_usage_of_intersight_server(
                        intersight_server=intersight_server["server"]
                    )
                )

                if power_usage_of_intersight_server_influxdb_data is not None:
                    influxdb_client.write_data(
                        data=power_usage_of_intersight_server_influxdb_data
                    )

            logger.info(
                "Waiting for the next polling of Cisco UCS servers managed by Intersight in %s seconds.\n",
                time_interval,
            )

            time.sleep(time_interval)
