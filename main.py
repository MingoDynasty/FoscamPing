"""==========================================================================
    Programmer: Mingo                                       Date: 2015-10-14
=========================================================================="""
import sys  # Provides access to command line arguments.
import os  # Provides access to operating system interfaces.
import logging  # Provides access to logging api.
import logging.config  # Provides access to logging configuration file.
import time  # Various time-related functions.
import argparse
import datetime
import math


from ConfigController import ConfigController
from PingController import PingController
from DatabaseController import DatabaseController
from EmailController import EmailController

from NamedTuples import Device, PingResult


class Controller:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
        self.configController = None
        self.databaseController = None
        self.pingController = None
        self.emailController = None
        self.emailConf = None
        self.pingCount = None
        return

    def __del__(self):
        return

    def main(self, argv):

        #
        # 1. Argument parsing
        #
        self.logger.debug("The total numbers of args passed to the script: %d " % len(argv))
        self.logger.debug("Args: " + str(argv))

        # TODO: flesh out argument parsing and help, -h
        # Parse command line arguments
        sDescription = "no description yet"

        sEpilog = "Returns exit code 0 on success, non-zero on error.\n\n" \
                  "Use app.conf to change script configuration.\n" \
                  "Use logging.conf to change logging information."

        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=sDescription,
                                         epilog=sEpilog)
        parser.add_argument('-host', help='hostname to ping')
        parser.add_argument('-f', '--file', help='file containing list of hosts to ping')
        parser.add_argument('-c', '--conf', default='app.conf', help='application config file to use (default: %(default)s)')
        args = parser.parse_args()
        self.logger.debug("Parsed args: " + str(args))

        appConfFile = os.path.join(os.path.dirname(__file__), args.conf)
        if not os.path.isfile(appConfFile):
            self.logger.error(appConfFile + " not found.")
            return

        hostnames = []
        if args.host:
            hostnames.append(args.host)

        # Also get the list of hosts from a file
        if args.file:
            if not os.path.isfile(args.file):
                self.logger.error("File not found: " + args.file)
                return
            else:
                with open(args.file, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if line:
                            hostnames.append(line)

        #
        # 2. Controller setup
        #

        # Get the configuration parameters
        self.configController = ConfigController()
        self.configController.loadConfiguration(appConfFile)

        # Establish a database connection
        self.databaseController = DatabaseController(True)
        self.databaseController.connect(self.configController.getDbConnectString())
        self.devices = self.databaseController.getDevices()

        # Get a ping controller instance
        self.pingController = PingController()
        self.pingCount = self.configController.getPingCount()

        # Setup email controller
        self.emailConf = self.configController.getEmailTuple()
        self.emailController = EmailController(self.emailConf.username, self.emailConf.password, self.emailConf.server, self.emailConf.port, self.emailConf.sender_name)

        #
        # 3. Script main run
        #
        # Finally we use the list of hostnames
        self.logic(hostnames)

        self.databaseController.disconnect()

        return 0

    # TODO: need a better function name than "logic"...
    def logic(self, hostnames):

        self.logger.debug("Hostnames: " + str(hostnames))

        # list of ping result tuples for failed pings
        failedPingResults = []

        # list of ping result tuples for successful pings
        successfulPingResults = []

        # list of ping result tuples from the database
        latestPingResults = self.databaseController.getLatestPingResults()

        # list of ping result tuples for successful pings that were previously failures
        failsuccessPingResults = []

        for hostname in hostnames:
            # If this is a new device then add it to the database
            if hostname not in self.devices:
                self.logger.debug("Found new device: " + hostname)
                device = Device(None, hostname, 1)
                newDevice = self.databaseController.addDevice(device)
                self.devices[hostname] = newDevice

            deviceId = self.devices[hostname].device_id

            pingResult = self.pingController.ping(hostname, self.pingCount, deviceId)
            if pingResult:
                successfulPingResults.append(pingResult)
            else:
                # New ping result with is_success=False
                pingResult = PingResult(device_id=deviceId, is_success=False)
                failedPingResults.append(pingResult)

            self.databaseController.addPingResult(pingResult)

        # Check if this device was previously down but is now up
        for pingResult in successfulPingResults:
            if pingResult.device_id in latestPingResults:
                prevIsSuccess = latestPingResults[pingResult.device_id].is_success
                datePinged = latestPingResults[pingResult.device_id].date_pinged
                now = datetime.datetime.now()
                minutesDownFor = math.ceil((now-datePinged).total_seconds()/60)
                if prevIsSuccess is not 1:
                    device = self.getDeviceById(pingResult.device_id)
                    self.logger.debug("Host '" + str(device.hostname) + "' was previously down for up to " + str(minutesDownFor) + " minutes but is now up.")
                    failsuccessPingResults.append(pingResult)

        # Check if this device was previously down and is still down
        # Copy failedPingResults into failedPingResultsCopy to avoid loop issues while deleting elements...
        # TODO: probably a better way of doing this
        failedPingResultsCopy = list(failedPingResults)
        for pingResult in failedPingResultsCopy:
            if pingResult.device_id in latestPingResults:
                prevIsSuccess = latestPingResults[pingResult.device_id].is_success
                if prevIsSuccess is not 1:
                    device = self.getDeviceById(pingResult.device_id)
                    self.logger.debug("Host '" + str(device.hostname) + "' was previously down and is still down.")
                    failedPingResults.remove(pingResult)

        # Send an email
        if failedPingResults or failsuccessPingResults:
            if not self.emailConf.enabled:
                self.logger.debug("Email is disabled. Skipping email...")
            else:
                self.logger.debug("Email is enabled: " + str(self.emailConf.enabled))
                subject = 'FoscamPing Email Controller'
                timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
                text = ''

                for failedPingResult in failedPingResults:
                    device = self.getDeviceById(failedPingResult.device_id)
                    text += timeNow + ' - Failed to ping: ' + device.hostname + "\n"

                for pingResult in failsuccessPingResults:
                    device = self.getDeviceById(pingResult.device_id)
                    datePinged = latestPingResults[pingResult.device_id].date_pinged
                    now = datetime.datetime.now()
                    minutesDownFor = math.ceil((now-datePinged).total_seconds()/60)
                    text += timeNow + ' - Previously down for up to ' + str(minutesDownFor) + ' minutes but is now up: ' + device.hostname + "\n"

                self.emailController.sendEmail(self.emailConf.send_to, subject, text)

        return

    def getDeviceById(self, device_id):
        """
        Helper function to get a Device tuple by device_id
        :param device_id: device_id to search for.
        :return: Device tuple if found, else None.
        """
        for hostname in self.devices:
            # if device.device_id == device_id:
            if self.devices[hostname].device_id == device_id:
                return self.devices[hostname]
        self.logger.error("Device id not found" + str(device_id))
        return None

if __name__ == "__main__":
    logConfFile = os.path.join(os.path.dirname(__file__), 'logging.conf')
    if not os.path.isfile(logConfFile):
        print(logConfFile + " not found.")
        exit()

    log_format = "%(asctime)-15s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
    logging.config.fileConfig(logConfFile)
    logger = logging.getLogger(__name__)

    logger.info('Starting FoscamPing...')
    controller = Controller()
    exitCode = controller.main(sys.argv)
    logger.info('...FoscamPing finished.')
    sys.exit(exitCode)

# end main
