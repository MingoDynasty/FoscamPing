from collections import namedtuple


class Device(namedtuple('Device', 'device_id, hostname, is_active')):
    pass


class PingResult(namedtuple('PingResult', 'device_id, date_pinged, packets_sent, packets_received, packets_lost, minimum_ping, maximum_ping, average_ping, is_success')):
    def __new__(cls, device_id, date_pinged=None, packets_sent=None, packets_received=None, packets_lost=None, minimum_ping=None, maximum_ping=None, average_ping=None, is_success=False):
        # add default values
        return super(PingResult, cls).__new__(cls, device_id, date_pinged, packets_sent, packets_received, packets_lost,
                                              minimum_ping, maximum_ping, average_ping, is_success)


class EmailConf(namedtuple('EmailConf', 'enabled, username, password, server, port, sender_name, send_to')):
    pass
