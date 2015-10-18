import logging  # Provides access to logging api.
import subprocess  # Provides ability to spawn new processes.


class PingController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __del__(self):
        return

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
