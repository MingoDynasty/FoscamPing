import logging  # Provides access to logging api.
import cx_Oracle
from collections import namedtuple


class DatabaseController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = None
        return

    def __del__(self):
        self.disconnect()
        return

    def connect(self, dbConnectString):
        self.logger.debug("Connecting to database...")
        self.db = cx_Oracle.connect(dbConnectString)
        self.logger.info("Connected to " + self.db.username + "@" + self.db.tnsentry)
        # return db
        return

    def disconnect(self):
        if self.db:
            self.logger.debug("Closing database...")
            self.db.close()
            self.logger.info("Database closed.")
        return

    def getDevices(self):
        """
        Get all Devices from the DEVICES table.
        :return: list of Device tuples.
        """
        self.logger.debug("Loading devices...")
        cursor = self.db.cursor()
        cursor.execute("SELECT device_id, hostname, is_active FROM DEVICES")

        Device = namedtuple('Device', 'device_id, hostname, is_active')
        devices = {}

        totalRows = 0
        for row in cursor:
            totalRows += 1
            device = Device(row[0], row[1], row[2])
            devices[row[1]] = device
            self.logger.debug("Found Device: " + str(device))

        self.logger.info("Found " + str(totalRows) + " Devices in Devices table.")
        cursor.close()
        return devices

    def addDevice(self, deviceTuple):
        """
        Add Device to DEVICES table.
        :return: none
        """
        cursor = self.db.cursor()

        self.logger.debug("Inserting Device: " + str(deviceTuple))

        cursor.prepare("INSERT INTO DEVICES (hostname, is_active) "
                       "VALUES (:hostname, 1)")
        cursor.execute(None, hostname=deviceTuple.hostname)

        cursor.close()
        self.logger.info("Inserted Device: " + deviceTuple.hostname)
        return
