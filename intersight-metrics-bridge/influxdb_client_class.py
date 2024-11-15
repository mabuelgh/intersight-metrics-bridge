"""This module defines InfluxDbClient class and methods to read/write data from/to InfluxDB database."""
#!/usr/bin/env python3

import pprint

from base_logger import logger
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


##############################################################################
#                           InfluxDBClient class                             #
##############################################################################


class InfluxDbClient:
    """
    InfluxDBClient class defines methods to connect to InfluxDB and read/write data from/to it.
    """

    def __init__(self, bucket, influxdb_url, org, token):
        logger.info(
            "Initializating InfluxDBClient instance with InfluxDB database at URL %s for bucket %s.\n",
            influxdb_url,
            bucket,
        )

        self._bucket = bucket
        self._client = InfluxDBClient(url=influxdb_url, token=token)
        self._influxdb_url = influxdb_url
        self._org = org

        logger.info(
            "InfluxDBClient instance was sucessfully initialized with InfluxDB database at URL %s for bucket %s.\n",
            influxdb_url,
            bucket,
        )

    def write_data(self, data, write_option=SYNCHRONOUS):
        """
        Write data to InfluxDB database.
        """
        if data is not None:
            logger.info(
                "Writing data to InfluxDB database at URL %s in bucket %s.\n",
                self._influxdb_url,
                self._bucket,
            )

            write_api = self._client.write_api(write_option)
            write_api.write(self._bucket, self._org, data, write_precision="s")

            logger.info(
                "==> Following data was written to InfluxDB database at URL %s in bucket %s:\n%s\n",
                self._influxdb_url,
                self._bucket,
                pprint.pformat(data),
            )

        else:
            logger.warning(
                "Skipping the data write to InfluxDB database at URL %s in bucket %s.\n",
                self._influxdb_url,
                self._bucket,
            )
