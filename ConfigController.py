import logging  # Provides access to logging api.
import sys
import cx_Oracle
import configparser
from NamedTuples import EmailConf


def newConfiguration(configfile):
    # Use a separate parser so the current configuration does not get corrupted.
    # newConfig = SafeConfigParser()
    newConfig = configparser.ConfigParser()

    # Database section
    newConfig.add_section('Database')
    newConfig.set('Database', 'HOST', 'host')
    newConfig.set('Database', 'PORT', 'port')
    newConfig.set('Database', 'SID', 'sid')
    newConfig.set('Database', 'USER', 'user')
    newConfig.set('Database', 'PASSWORD', 'password')

    # Write the configuration file template
    with open(configfile, 'w') as configfile:
        newConfig.write(configfile)


class ConfigController:
    def __init__(self):
        # self.config = SafeConfigParser()
        self.logger = logging.getLogger(__name__)
        self.config = configparser.ConfigParser()
        return

    def __del__(self):
        return

    def loadConfiguration(self, configfile):
        self.logger.debug("Loading config file: " + configfile)
        self.config.read(configfile)
        self.logger.info("Loaded config file: " + configfile)

    #
    # Application Section
    #
    def getPingCount(self):
        value = self.config.get('Application', 'ping_count')
        int_value = int(value)
        if int_value < 1:
            self.logger.error("Invalid ping_count: " + value)
            raise ValueError
        return int_value

    #
    # Database Section
    #
    def getDbConnectString(self):
        connectString = "%s/%s@%s:%s/%s" % (
            self.getDbUser(), self.getDbPassword(), self.getDbHost(), self.getDbPort(), self.getDbSid())
        return connectString

    def getDbDsn(self):
        dsn = cx_Oracle.makedsn(self.getDbHost(), self.getDbPort(), self.getDbSid())
        return dsn

    def getDbHost(self):
        return self.config.get('Database', 'Host')

    def getDbPassword(self):
        return self.config.get('Database', 'Password')

    def getDbPort(self):
        return self.config.get('Database', 'Port')

    def getDbSid(self):
        return self.config.get('Database', 'Sid')

    def getDbUser(self):
        return self.config.get('Database', 'user')

    def getDefaultParam(self, param):
        return self.config.get('Defaults', param)

    #
    # Email Section
    #
    def getEmailEnabled(self):
        return self.config.get('Email', 'enabled').lower() == 'true'

    def getEmailUsername(self):
        return self.config.get('Email', 'username')

    def getEmailPassword(self):
        return self.config.get('Email', 'password')

    def getEmailServer(self):
        return self.config.get('Email', 'server')

    def getEmailPort(self):
        return self.config.get('Email', 'port')

    def getEmailSenderName(self):
        return self.config.get('Email', 'sender_name')

    def getEmailSendTo(self):
        return self.config.get('Email', 'send_to')

    def getEmailDict(self):
        emailDict = {'enabled': self.getEmailEnabled(),
                     'username': self.getEmailUsername(), 'password': self.getEmailPassword(),
                     'server': self.getEmailServer(), 'port': self.getEmailPort(),
                     'sender_name': self.getEmailSenderName(),
                     'send_to': self.getEmailSendTo()}
        return emailDict

    def getEmailTuple(self):
        emailTuple = EmailConf(self.getEmailEnabled(), self.getEmailUsername(), self.getEmailPassword(), self.getEmailServer(), self.getEmailPort(), self.getEmailSenderName(), self.getEmailSendTo())
        return emailTuple


# end class Configuration ######

if __name__ == "__main__":

    if len(sys.argv) > 1:
        config = ConfigController()
        newConfiguration(sys.argv[1])
    else:
        print("You must specify a filename to create a new configuration file.")
