import logging  # Provides access to logging api.
import smtplib


class EmailController:
    def __init__(self, username, password, server, port, sender_name):
        self.logger = logging.getLogger(__name__)
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.sender_name = sender_name
        return

    def __del__(self):
        return

    def sendEmail(self, send_to, subject, text):

        self.logger.debug("Trying smtp...")
        server = smtplib.SMTP(self.server, self.port)

        self.logger.debug("Trying ehlo...")
        server.ehlo()

        self.logger.debug("Trying starttls...")
        server.starttls()

        self.logger.debug("Trying login...")
        server.login(self.username, self.password)

        body = '\r\n'.join(['To: %s' % send_to,
                            'From: %s' % self.sender_name,
                            'Subject: %s' % subject,
                            '', text])

        try:
            self.logger.debug("Attempting to send....")
            server.sendmail(self.username, [send_to], body)
            self.logger.debug("Successfully sent.")
        except smtplib.SMTPException:
            self.logger.error("Failed to send.")
            return False

        server.quit()
        return True

# end EmailController
