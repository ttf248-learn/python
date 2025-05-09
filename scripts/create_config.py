from cryptography.fernet import Fernet
import json
import os

def create_config():
    # 创建配置目录
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
    os.makedirs(config_dir, exist_ok=True)
    
    # 生成新的加密密钥
    key = Fernet.generate_key()
    key_path = os.path.join(config_dir, '.key')
    
    # 保存密钥到文件
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    
    # 创建配置数据
    config = {
        "SMTP_SERVER": "smtpdm.aliyun.com",
        "SMTP_PORT": 465,
        "EMAIL_ADDRESS": "your_email@example.com",
        "EMAIL_PASSWORD": "your_password"
    }
    
    # 加密配置数据
    f = Fernet(key)
    encrypted_data = f.encrypt(json.dumps(config).encode())
    
    # 保存加密的配置
    config_path = os.path.join(config_dir, 'mail_config.enc')
    with open(config_path, 'wb') as config_file:
        config_file.write(encrypted_data)
    
    print(f"配置文件已创建：{config_path}")
    print(f"密钥文件已创建：{key_path}")
    print("\n请修改配置文件中的邮箱地址和密码！")
    print("注意：请确保 .gitignore 中包含以下内容：")
    print("scripts/config/.key")
    print("scripts/config/mail_config.enc")

if __name__ == "__main__":
    create_config()