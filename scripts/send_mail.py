import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from cryptography.fernet import Fernet
import json

def load_encrypted_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'mail_config.enc')
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', '.key')
    
    if not os.path.exists(config_path) or not os.path.exists(key_path):
        raise FileNotFoundError("配置文件或密钥文件不存在，请先运行 create_config.py 创建配置")
    
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
    
    f = Fernet(key)
    with open(config_path, 'rb') as config_file:
        encrypted_data = config_file.read()
    
    decrypted_data = f.decrypt(encrypted_data)
    config = json.loads(decrypted_data.decode())
    return config

# Email configuration from encrypted config
config = load_encrypted_config()
SMTP_SERVER = config.get("SMTP_SERVER", "smtpdm.aliyun.com")
SMTP_PORT = int(config.get("SMTP_PORT", 465))  # Default to 465 if not set
EMAIL_ADDRESS = config.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = config.get("EMAIL_PASSWORD")

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise ValueError("配置文件中必须包含 EMAIL_ADDRESS 和 EMAIL_PASSWORD")

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
            print("邮件发送成功！")

    except Exception as e:
        print(f"邮件发送失败: {e}")

# Example usage
if __name__ == "__main__":
    recipient = "10462443139999@qq.com"  # Replace with recipient's email
    subject = "邮件服务测试"
    body = "这是一封测试邮件。"
    send_email(recipient, subject, body)