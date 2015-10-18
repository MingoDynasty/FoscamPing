"""==========================================================================
    Programmer: Mingo                                       Date: 2015-10-14
=========================================================================="""
import sys  # Provides access to command line arguments.
import os  # Provides access to operating system interfaces.
import logging  # Provides access to logging api.
import logging.config  # Provides access to logging configuration file.
import time  # Various time-related functions.

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
        self.emailDict = {}
        return

    def __del__(self):
        return

    def main(self, argv):

        # Very basic arg parsing...
        total = len(argv)
        self.logger.debug("The total numbers of args passed to the script: %d " % total)
        for i in range(0, total):
            self.logger.debug("Arg[" + str(i) + "]: " + argv[i])

        conf_filename = "app.conf"
        if not os.path.isfile(conf_filename):
            self.logger.error(conf_filename + " not found.")
            return

        # Get the configuration parameters
        self.configController = ConfigController()
        self.configController.loadConfiguration(conf_filename)

        # Establish a database connection
        self.databaseController = DatabaseController(True)
        self.databaseController.connect(self.configController.getDbConnectString())
        self.devices = self.databaseController.getDevices()

        # Get a ping controller instance
        self.pingController = PingController()

        # Setup email controller
        self.emailDict = self.configController.getEmailDict()
        self.emailController = EmailController(self.emailDict['username'], self.emailDict['password'], self.emailDict['server'], self.emailDict['port'], self.emailDict['sender_name'])

        hostnames = []

        # Iterate over all args
        for i in range(1, total):
            hostname = argv[i]
            hostnames.append(hostname)

        # Also get the list of hosts from a file
        filename = 'list_of_hosts'
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    hostnames.append(line)

        # Finally we use the list of hostnames
        self.logic(hostnames)

        self.databaseController.disconnect()

        return 0

    # TODO: need a better function name than "logic"...
    def logic(self, hostnames):

        # list of ping result tuples for failed pings
        failedPingResults = []

        # list of ping result tuples for successful pings
        successfulPingResults = []

        # list of ping result tuples from the database
        latestPingResults = self.databaseController.getLatestPingResults()

        # list of ping result tuples for successful pings that were previously failures
        failsuccessPingResults = []

        for hostname in hostnames:
            if hostname not in self.devices:
                self.logger.debug("Found new device: " + hostname)
                device = Device(None, hostname, 1)
                self.databaseController.addDevice(device)
                self.devices[hostname] = device

            deviceId = self.devices[hostname].device_id

            pingResult = self.pingController.ping(hostname, deviceId)
            if pingResult:
                successfulPingResults.append(pingResult)
            else:
                # New ping result with is_success=False
                pingResult = PingResult(device_id=deviceId, is_success=False)
                failedPingResults.append(pingResult)

            self.databaseController.addPingResult(pingResult)

        for pingResult in successfulPingResults:
            prevIsSuccess = latestPingResults[pingResult.device_id].is_success
            if prevIsSuccess is not 1:
                self.logger.debug("Device " + str(pingResult.device_id) + " was previously down but is now up.")
                failsuccessPingResults.append(pingResult)

        if failedPingResults or failsuccessPingResults:
            # Send an email
            if not self.emailDict['enabled']:
                self.logger.debug("Email is disabled. Skipping email...")
            else:
                self.logger.debug("Email is enabled: " + str(self.emailDict['enabled']))
                subject = 'FoscamPing Email Controller'
                timeNow = time.strftime('%Y-%m-%d %H:%M:%S')
                text = ''

                for failedPingResult in failedPingResults:
                    device = self.getDeviceById(failedPingResult.device_id)
                    text += timeNow + ' - Failed to ping: ' + device.hostname + "\n"

                for pingResult in failsuccessPingResults:
                    device = self.getDeviceById(pingResult.device_id)
                    text += timeNow + ' - Previously down but is now up: ' + device.hostname + "\n"

                self.emailController.sendEmail(self.emailDict['send_to'], subject, text)

        return

    def getDeviceById(self, device_id):
        for hostname in self.devices:
            # if device.device_id == device_id:
            if self.devices[hostname].device_id == device_id:
                return self.devices[hostname]
        self.logger.error("Device id not found" + str(device_id))
        return None

if __name__ == "__main__":
    log_format = "%(asctime)-15s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger(__name__)

    logger.info('Starting FoscamPing...')
    controller = Controller()
    exitCode = controller.main(sys.argv)
    logger.info('...FoscamPing finished.')
    sys.exit(exitCode)

# end main
