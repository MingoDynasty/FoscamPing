import logging  # Provides access to logging api.
import subprocess  # Provides ability to spawn new processes.
from NamedTuples import PingResult


class PingController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        return

    def __del__(self):
        return

    # TODO: this function takes in a deviceId for now... but that should not be the case
    def ping(self, hostname, deviceId):
        """
        Ping a host. Note that this implementation may or may not work on non-Windows operating systems.
        :param hostname: hostname to ping
        :return: PingResult on successful ping, else None.
        """
        self.logger.debug("Pinging hostname: " + hostname)
        cmd = "ping -n 1 " + hostname

        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            pingResult = PingResult(device_id=deviceId, is_success=True)
            self.logger.info("Successfully pinged: " + hostname)
            return pingResult  # if we make it here, then the command succeeded

        # exception is thrown on non-zero exits, so this must mean the command failed
        except subprocess.CalledProcessError as e:
            # TODO: may want to return e object or something
            self.logger.warning("Failed to ping: " + hostname)
            return None

# end PingController
