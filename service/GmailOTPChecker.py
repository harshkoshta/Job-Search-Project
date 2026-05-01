import imaplib
import email
import re

class GmailOTPChecker:
    def __init__(self, gmail_address, app_password):
        self.mail = imaplib.IMAP4_SSL("imap.gmail.com")
        self.gmail_address = gmail_address
        self.app_password = app_password

    def login(self):
        try:
            self.mail.login(self.gmail_address, self.app_password)
            print("Login successful!")
        except imaplib.IMAP4.error as e:
            print(f"Login failed: {e}")

    def otpcheck(self):
        self.mail.select("inbox")
        status, data = self.mail.search(None, 'FROM "login@indeed.com"')

        for eid in reversed(data[0].split()):
            status, msg_data = self.mail.fetch(eid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            body = msg.get_payload(decode=True) or b""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True)
                        break

            otp = re.search(r'\b\d{6}\b', body.decode("utf-8", errors="ignore"))
            self.mail.logout()
            if otp:
                print(f"🔑 OTP: {otp.group()}")
                return otp.group()
        return None