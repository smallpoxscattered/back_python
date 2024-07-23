import requests
import json
import os
from PIL import Image

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

    def upload_image(self, image_path, size):
        if not self.jwt:
            print("未登录，请先调用 login 方法")
            return None

        url = f"{self.base_url}/upload"
        headers = {
            "Authorization": f"Bearer {self.jwt}"
        }

        # 输出所有需要的信息
        print(f"图片路径 {image_path}")
        print(f"图片大小 {size}")
        print(f"图片路径 {self.base_url}")

        # 准备文件和数据
        files = {
            'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/png')
        }
        data = {
            'size': json.dumps(size)
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                print("图片上传成功")
                return response.json()
            else:
                print(f"图片上传失败: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"请求发生错误: {str(e)}")
            return None

    def test_upload_image(self):
        # 准备测试数据
        image_path = r"data\labels_colored\0000051.png"
        size = [15, 15]

        # 发送图片上传请求
        response = self.upload_image(image_path, size)
        
        if response:
            print("响应内容:")
            data = json.dumps(response, indent=2, ensure_ascii=False)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print("图片上传失败")

    def test_add_game_record(self):
        # 准备测试数据
        test_data = {
            "level_id": "1",
            "completion_time": 1.5,
            "score": 10,
            "difficulty": 2
        }

        # 发送添加游戏记录的请求
        response = self.send_authenticated_request("add_record", method="POST", data=test_data)
        
        if response:
            print(f"状态码: {response.status_code}")
            print("响应内容:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))

            # 检查响应是否符合预期
            if response.status_code == 201:
                print("测试成功：游戏记录添加成功")
            else:
                print(f"测试失败：预期状态码201，实际获得{response.status_code}")
        else:
            print("请求失败，未收到响应")

# 使用示例
if __name__ == "__main__":
    client = ApiClient("http://0.0.0.0:8852/api")
    
    # 登录
    if client.login("string", "string"):
        print("登录成功")
        # client.test_upload_image()
        client.test_add_game_record()
        data = {
            'level_id': '1',
        }
        response = client.send_authenticated_request('leaderboard', 'POST', data)
        print(response.json())
    else:
        print("登录失败")