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


class Controller:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.devices = {}
        return

    def __del__(self):
        return

    def main(self, argv):

        bDebug = True
        total = len(argv)
        if bDebug:
            self.logger.debug("The total numbers of args passed to the script: %d " % total)
            for i in range(0, total):
                self.logger.debug("Arg[" + str(i) + "]: " + argv[i])

        # Get the configuration parameters
        configController = ConfigController()
        configController.loadConfiguration("database.conf")

        # Establish a database connection
        databaseController = DatabaseController()
        databaseController.connect(configController.getDbConnectString())
        self.devices = databaseController.getDevices()

        for i in range(1, total):
            hostname = argv[i]
            self.logic(hostname)

        # Atlernatively, get the list of hosts from a file
        filename = 'list_of_hosts'
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    # self.logger.debug(line)
                    self.logic(line)

        self.logger.debug("Done.")
        return 0

    # TODO: need a better function name than "logic"...
    def logic(self, hostname):
        pingController = PingController()

        if hostname not in self.devices:
            self.logger.debug("Found new device: " + hostname)

        # pingResult = pingController.ping(hostname)
        # if pingController.ping(hostname):
            # self.logger.debug(hostname + ' is up!')
        # else:
        #     self.logger.debug(hostname + ' is down.')


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
