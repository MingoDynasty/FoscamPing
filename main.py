"""==========================================================================
    Programmer: Mingo                                       Date: 2015-10-14
=========================================================================="""
import sys  # Provides access to command line arguments.
import os  # Provides access to operating system interfaces.
import logging  # Provides access to logging api.
import logging.config  # Provides access to logging configuration file.

from ConfigController import ConfigController
from PingController import PingController
from DatabaseController import DatabaseController

from NamedTuples import Device, PingResult


class Controller:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
        self.configController = None
        self.databaseController = None
        self.pingController = None
        return

    def __del__(self):
        return

    def main(self, argv):

        # Very basic arg parsing...
        total = len(argv)
        self.logger.debug("The total numbers of args passed to the script: %d " % total)
        for i in range(0, total):
            self.logger.debug("Arg[" + str(i) + "]: " + argv[i])

        # Get the configuration parameters
        self.configController = ConfigController()
        self.configController.loadConfiguration("database.conf")

        # Establish a database connection
        self.databaseController = DatabaseController(True)
        self.databaseController.connect(self.configController.getDbConnectString())
        self.devices = self.databaseController.getDevices()

        # Get a ping controller instance
        self.pingController = PingController()

        # Iterate over all args
        for i in range(1, total):
            hostname = argv[i]
            self.logic(hostname)

        # Alternatively, get the list of hosts from a file
        filename = 'list_of_hosts'
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    # self.logger.debug(line)
                    self.logic(line)

        self.databaseController.disconnect()

        return 0

    # TODO: need a better function name than "logic"...
    def logic(self, hostname):

        if hostname not in self.devices:
            self.logger.debug("Found new device: " + hostname)
            device = Device(None, hostname, 1)
            self.databaseController.addDevice(device)
            self.devices[hostname] = device

        deviceId = self.devices[hostname].device_id

        pingResult = self.pingController.ping(hostname, deviceId)
        if not pingResult:
            pingResult = PingResult(device_id=deviceId, is_success=False)

        self.databaseController.addPingResult(pingResult)
        return

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
