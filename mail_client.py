# -*- coding: utf-8 -*-
"""
DuckMail 临时邮箱客户端
功能：通过 DuckMail API 注册临时邮箱，接收验证码邮件
API 文档：https://api.duckmail.sbs
"""

import requests
import time
import re
import random
import string

# DuckMail API 配置
BASE_URL = "https://api.duckmail.sbs"  # DuckMail API 地址
PROXY_URL = "http://127.0.0.1:7890"    # 代理地址（与主程序保持一致）

class DuckMailClient:
    """DuckMail 临时邮箱客户端类"""
    
    def __init__(self):
        """初始化邮箱客户端"""
        self.proxies = {"http": PROXY_URL, "https": PROXY_URL}
        self.email = None          # 邮箱地址
        self.password = None       # 邮箱密码
        self.account_id = None     # 账号 ID
        self.token = None          # 认证 Token

    def register(self):
        """
        注册临时邮箱账号
        返回：True=注册成功，False=注册失败
        """
        # 获取可用的邮箱域名
        domain = "duck.com"  # 默认域名
        try:
            resp = requests.get(f"{BASE_URL}/domains", proxies=self.proxies, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if 'hydra:member' in data and len(data['hydra:member']) > 0:
                    domain = data['hydra:member'][0]['domain']  # 使用第一个可用域名
        except:
            pass  # 如果获取失败，使用默认域名

        # 生成随机邮箱地址和密码
        rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))  # 10位随机字符串
        timestamp = str(int(time.time()))[-4:]  # 时间戳后4位
        self.email = f"t{timestamp}{rand_str}@{domain}"
        self.password = f"Pwd{rand_str}{timestamp}"

        print(f"[Mail] Register: {self.email}")

        # 向 API 注册账号
        try:
            reg = requests.post(f"{BASE_URL}/accounts",
                              json={"address": self.email, "password": self.password},
                              proxies=self.proxies, timeout=15)
            if reg.status_code in [200, 201]:
                self.account_id = reg.json().get('id')
                return True
            return False
        except:
            return False

    def login(self):
        """
        登录邮箱账号，获取认证 Token
        返回：True=登录成功，False=登录失败
        """
        if not self.email: return False
        try:
            login = requests.post(f"{BASE_URL}/token",
                                json={"address": self.email, "password": self.password},
                                proxies=self.proxies, timeout=15)
            if login.status_code == 200:
                self.token = login.json().get('token')
                return True
            return False
        except:
            return False

    def wait_for_code(self, timeout=300):
        """
        等待并获取邮件中的验证码
        参数：timeout - 超时时间（秒），默认 300 秒
        返回：验证码字符串，如果超时则返回 None
        """
        # 如果没有 Token，先登录
        if not self.token:
            if not self.login(): return None

        print(f"[Mail] Waiting for code ({timeout}s)...")
        headers = {"Authorization": f"Bearer {self.token}"}
        start_time = time.time()

        # 循环检查新邮件
        while (time.time() - start_time) < timeout:
            try:
                # 获取邮件列表
                resp = requests.get(f"{BASE_URL}/messages", headers=headers, proxies=self.proxies, timeout=10)
                if resp.status_code == 200:
                    msgs = resp.json().get('hydra:member', [])
                    if msgs:
                        # 获取最新邮件的详细内容
                        msg_id = msgs[0]['id']
                        detail = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers, proxies=self.proxies, timeout=10)
                        data = detail.json()
                        content = data.get('text') or data.get('html') or ""

                        # 从邮件内容中提取验证码
                        code = self._extract_code(content)
                        if code:
                            print(f"[Mail] Code: {code}")
                            return code
            except:
                pass

            time.sleep(3)  # 每 3 秒检查一次

        return None  # 超时返回 None

    def _extract_code(self, text):
        """
        从邮件内容中提取验证码
        参数：text - 邮件文本内容
        返回：验证码字符串，如果未找到则返回 None
        """
        # 方法1: 查找"验证码"、"code"等关键词后的 4-8 位字符
        pattern_context = r'(?:验证码|code|verification|passcode|pin).*?[:：]\s*([A-Za-z0-9]{4,8})\b'
        match = re.search(pattern_context, text, re.IGNORECASE | re.DOTALL)
        if match: return match.group(1)

        # 方法2: 查找 6 位纯数字（常见的验证码格式）
        digits = re.findall(r'\b\d{6}\b', text)
        if digits: return digits[0]

        return None  # 未找到验证码

    def delete(self):
        """
        删除邮箱账号（清理资源）
        注意：通常不需要手动调用，邮箱会自动过期
        """
        if not self.account_id or not self.token: return
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            requests.delete(f"{BASE_URL}/accounts/{self.account_id}", headers=headers, proxies=self.proxies)
        except:
            pass
