import requests
import json

class ApiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.jwt = None

    def login(self, username, password):
        url = f"{self.base_url}/login"
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            self.jwt = response_data.get("access_token")
            return True
        else:
            print(f"登录失败: {response.status_code} - {response.text}")
            return False

    def send_authenticated_request(self, endpoint, method="GET", data=None):
        if not self.jwt:
            print("未登录，请先调用 login 方法")
            return None

        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.jwt}"
        }

        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"不支持的 HTTP 方法: {method}")
            return None

        if response.status_code == 401:
            print("认证失败，可能需要重新登录")
            return None

        return response

# 使用示例
if __name__ == "__main__":
    client = ApiClient("http://10.33.34.196:8852/api")
    
    # 登录
    if client.login("string", "string"):
        print("登录成功")
        data = {
            'serial_number': 1
        }
        # 发送一个认证请求
        response = client.send_authenticated_request("getMap", 'POST', data=data)
        if response:
            print(f"请求成功: {response.status_code}")
            print(f"响应内容: {response.text.keys()}")
    else:
        print("登录失败")