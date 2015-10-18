import logging  # Provides access to logging api.
import cx_Oracle


class DatabaseController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db = None

    def __del__(self):
        if self.db:
            self.logger.debug("Closing database...")
            self.db.close()
            self.logger.info("Database closed.")
        return

    def connect(self, dbConnectString):
        self.logger.debug("Connecting to database...")
        self.db = cx_Oracle.connect(dbConnectString)
        self.logger.info("Connected to " + self.db.username + "@" + self.db.tnsentry)
        # return db
        return
