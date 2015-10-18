__author__ = 'User'
from collections import namedtuple


class Device(namedtuple('Device', 'device_id, hostname, is_active')):
    pass
