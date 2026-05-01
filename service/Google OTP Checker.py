import imaplib
import email
import re

# Use SSL - standard IMAP4 without SSL will often fail or be rejected
mail = imaplib.IMAP4_SSL("imap.gmail.com")

gmail_address = "mcafreedec@gmail.com"
# Replace with the 16-character App Password generated in Step 2
app_password = "uddm btoj qpur xgys"

try:
    mail.login(gmail_address, app_password)
    print("Login successful!")
except imaplib.IMAP4.error as e:
    print(f"Login failed: {e}")
mail.select("inbox")
status, data = mail.search(None, 'FROM "login@indeed.com"')

for eid in reversed(data[0].split()):
    status, msg_data = mail.fetch(eid, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])

    body = msg.get_payload(decode=True) or b""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True)
                break

    otp = re.search(r'\b\d{6}\b', body.decode("utf-8", errors="ignore"))
    if otp:
        print(f"🔑 OTP: {otp.group()}")
        break

mail.logout()