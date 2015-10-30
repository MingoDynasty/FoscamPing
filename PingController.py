import logging  # Provides access to logging api.
import subprocess  # Provides ability to spawn new processes.
import shlex  # Simple Lexical Analysis
import re  # Regular Expressions
from NamedTuples import PingResult
from PingResultPojo import PingResultPojo


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
        # cmd = "ping -n 1 " + hostname  # original command
        cmd = "ping " + hostname  # original command
        cmd_list = shlex.split(cmd)  # split the command in a list

        try:
            output = subprocess.check_output(cmd_list, stderr=subprocess.STDOUT, shell=False, universal_newlines=False)

            # entirely possible to get a successful return code but the ping actually failed
            # parse the output and collect additional data from it
            output_decoded = output.decode("utf-8")
            pingResultPojo = self.parse(output_decoded)
            if not pingResultPojo:
                self.logger.error("Failed to ping: " + hostname)
                return None

            # extract pojo and put into namedtuple
            pingResult = PingResult(device_id=deviceId,
                                    date_pinged=None,
                                    packets_sent=float(pingResultPojo.packets_sent),
                                    packets_received=float(pingResultPojo.packets_received),
                                    packets_lost=float(pingResultPojo.packets_lost),
                                    minimum_ping=float(pingResultPojo.minimum_ping),
                                    maximum_ping=float(pingResultPojo.maximum_ping),
                                    average_ping=float(pingResultPojo.average_ping),
                                    is_success=True)
            self.logger.info("Successfully pinged: " + hostname)
            return pingResult  # if we make it here, then the command succeeded

        # exception is thrown on non-zero exits, so this must mean the command failed
        except subprocess.CalledProcessError as e:
            # TODO: may want to return e object or perhaps just raise and let caller handle the exception
            self.logger.warning("Failed to ping: " + hostname)
            self.logger.debug("Output: %s" % e.output.strip())
            return None

    def parse(self, ping_output):
        """
        Parse the ping output.
        :param ping_output: string to parse.
        :return: PingResultPojo with ping result data, else None on failure.
        """
        if 'Destination host unreachable' in ping_output:
            self.logger.debug("Destination host was unreachable.")
            return None

        # can usually get these
        sent = ping_output.split('Sent = ')[1].split(',')[0]
        received = ping_output.split('Received = ')[1].split(',')[0]
        lost = ping_output.split('Lost = ')[1].split(',')[0]
        lostTotal = ping_output.split('Lost = ')[1].split(' ')[0]
        lostPercent = ping_output.split('%')[0].split('(')[1]

        # might not get these if there's "Destination host unreachable"
        min_ping = ping_output.split('Minimum = ')[1].split('ms')[0]
        max_ping = ping_output.split('Maximum = ')[1].split('ms')[0]
        avg_ping = ping_output.split('Average = ')[1].split('ms')[0]

        # package results into pojo
        pingResultPojo = PingResultPojo()
        pingResultPojo.packets_sent = sent
        pingResultPojo.packets_received = received
        pingResultPojo.packets_lost = lostTotal
        pingResultPojo.minimum_ping = min_ping
        pingResultPojo.maximum_ping = max_ping
        pingResultPojo.average_ping = avg_ping
        pingResultPojo.is_success = True
        self.logger.debug(vars(pingResultPojo))
        return pingResultPojo

# end PingController
