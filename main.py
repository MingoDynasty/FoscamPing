"""==========================================================================
    Programmer: Mingo                                       Date: 2015-10-14
=========================================================================="""
import sys  # Provides access to command line arguments.
import os  # Provides access to operating system interfaces.
import subprocess  # Provides ability to spawn new processes.
import logging  # Provides access to logging api.
import logging.config  # Provides access to logging configuration file.
import cx_Oracle
from config import Configuration


class Controller:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
        config = Configuration()
        config.loadConfiguration("database.conf")

        # Establish a database connection
        self.logger.debug("Connecting to database...")
        db = cx_Oracle.connect(config.getDbConnectString())
        self.logger.info("Connected to host: " + config.getDbHost())

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
        if self.ping(hostname):
            self.logger.debug(hostname + ' is up!')
        else:
            self.logger.debug(hostname + ' is down.')

    def ping(self, hostname):
        """
        Ping a host. Note that this implementation may or may not work on non-Windows operating systems.
        :param hostname: hostname to ping
        :return: true on successful ping, else false.
        """
        self.logger.debug("Pinging hostname: " + hostname)
        cmd = "ping -n 1 " + hostname

        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            return True  # if we make it here, then the command succeeded

        # exception is thrown on non zero exits, so this must mean the command failed
        except subprocess.CalledProcessError as e:
            # TODO: may want to return e object or something
            return False


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
