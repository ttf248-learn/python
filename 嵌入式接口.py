import requests

import requests

class FaceABCClient:
    def __init__(self, device_no, token=None, message_url=None):
        self.device_no = device_no
        self.token = token
        self.message_url = message_url
        self.base_url = "http://checkin.faceabc.cn:801/api"

    def login(self, job_number, password, camra_count, version):
        """
        使用提供的参数执行 POST 请求，并返回响应正文。
        """
        url = f"{self.base_url}/device/login"

        data = {
            "job_number": job_number,
            "password": password,
            "camra_count": camra_count,
            "version": version,
            "device_no": self.device_no
        }

        response = requests.post(url, json=data)

        response_json = response.json()

        self.token = response_json["token"]
        self.message_url = response_json["message_url"]

        return response_json

    def check_upgrade(self):
        """
        使用提供的参数执行 POST 请求，并返回响应正文。
        """
        url = f"{self.base_url}/upgrade/version"

        headers = {
            "device_no": self.device_no,
            "token": self.token
        }

        response = requests.post(url, headers=headers)

        return response.json()



def main():
    device_no = "your_device_no"
    job_number = "600002"
    password = "123456"
    camra_count = 2
    version = "1.1"

    client = FaceABCClient(device_no)

    response_json = client.login(job_number, password, camra_count, version)

    print("响应正文：")
    print(response_json)
    print("token：", client.token)
    print("message_url：", client.message_url)

if __name__ == "__main__":
    main()

