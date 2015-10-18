import logging  # Provides access to logging api.
import cx_Oracle
from NamedTuples import Device


class DatabaseController:
    def __init__(self, willCommit):
        self.logger = logging.getLogger(__name__)
        self.db = None
        self.willCommit = willCommit
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
            if self.willCommit:
                self.logger.debug("Committing changes...")
                self.db.commit()
            else:
                self.logger.debug("Rolling back changes...")
                self.db.rollback()

            self.logger.debug("Closing database...")
            self.db.close()
            self.db = None
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
        Add a Device to DEVICES table.
        :param deviceTuple: device to add.
        :return:
        """
        cursor = self.db.cursor()

        self.logger.debug("Inserting Device: " + str(deviceTuple))

        cursor.prepare("INSERT INTO DEVICES (hostname, is_active) "
                       "VALUES (:hostname, 1)")
        cursor.execute(None, hostname=deviceTuple.hostname)

        cursor.close()
        self.logger.info("Inserted Device: " + deviceTuple.hostname)
        return

    def addPingResult(self, pingResultTuple):
        """
        Add a PingResult to PING_RESULTS table.
        :param pingResultTuple: ping result to add.
        :return:
        """
        cursor = self.db.cursor()

        self.logger.debug("Inserting PingResult: " + str(pingResultTuple))

        cursor.prepare(
            "INSERT INTO PING_RESULTS (device_id, packets_sent, packets_received, packets_lost, minimum_ping, maximum_ping, average_ping, is_success) "
            "VALUES (:device_id, :packets_sent, :packets_received, :packets_lost, :minimum_ping, :maximum_ping, :average_ping, :is_success)")
        cursor.execute(None, device_id=pingResultTuple.device_id,
                       packets_sent=pingResultTuple.packets_sent,
                       packets_received=pingResultTuple.packets_received,
                       packets_lost=pingResultTuple.packets_lost,
                       minimum_ping=pingResultTuple.minimum_ping,
                       maximum_ping=pingResultTuple.maximum_ping,
                       average_ping=pingResultTuple.average_ping,
                       is_success=pingResultTuple.is_success)

        cursor.close()
        self.logger.debug("Inserted PingResult: " + str(pingResultTuple))
        return

# end DatabaseController
