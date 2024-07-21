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

    def test_add_game_record(self):
        # 准备测试数据
        test_data = {
            "level_id": "1",
            "completion_time": 120.5,
            "score": 1000,
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
        # client.test_add_game_record()
    else:
        print("登录失败")