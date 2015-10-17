import sys
import cx_Oracle
# from ConfigParser import SafeConfigParser
import configparser


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


class Configuration:
    def __init__(self):
        # self.config = SafeConfigParser()
        self.config = configparser.ConfigParser()

    def __del__(self):
        return

    def loadConfiguration(self, configfile):
        self.config.read(configfile)

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


# end class Configuration ######

if __name__ == "__main__":

    if len(sys.argv) > 1:
        config = Configuration()
        newConfiguration(sys.argv[1])
    else:
        print("You must specify a filename to create a new configuration file.")
