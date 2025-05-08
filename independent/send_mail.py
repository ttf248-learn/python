import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
SMTP_SERVER = "smtpdm.aliyun.com"
SMTP_PORT = 465  # Use 25, 80, or 465 (SSL)
EMAIL_ADDRESS = "xiangtl@mail.ttf248.life	"  # Replace with your email address
EMAIL_PASSWORD = "TeTrbDRnEr5lj6hU"  # Replace with your email password

def send_email(to_email, subject, body):
    try:
        # Create a MIMEText email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")

# Example usage
if __name__ == "__main__":
    recipient = "10462443139999@qq.com"  # Replace with recipient's email
    subject = "邮件服务测试"
    body = "这是一封测试邮件。"
    send_email(recipient, subject, body)