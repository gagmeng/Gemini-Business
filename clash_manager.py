# -*- coding: utf-8 -*-
"""
Clash 代理管理器
功能：启动和管理 Clash 核心，自动检测可用节点
注意：当前项目已配置为使用外部代理（Clash Verge），此文件保留但不使用
"""

import subprocess
import requests
import yaml
import time
import os
import atexit
import sys
import random
import urllib.parse

class ClashManager:
    """Clash 代理管理器类（已弃用，保留用于参考）"""
    
    def __init__(self, executable="clash.exe", config="local.yaml", runtime_config="config_runtime.yaml", port=17890, api_port=9090):
        """
        初始化 Clash 管理器
        参数：
            executable - Clash 可执行文件路径
            config - 配置文件路径
            runtime_config - 运行时配置文件路径
            port - 代理端口
            api_port - API 端口
        """
        self.executable = executable
        self.config = config
        self.runtime_config = runtime_config
        self.port = port
        self.api_port = api_port
        self.api_url = f"http://127.0.0.1:{api_port}"
        self.process = None
        self._prepare_config()

    def _prepare_config(self):
        """准备运行时配置文件（从 local.yaml 生成 config_runtime.yaml）"""
        if not os.path.exists(self.config):
            raise FileNotFoundError(f"Config not found: {self.config}")

        # 读取配置文件
        with open(self.config, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)

        # 修改端口配置
        cfg['mixed-port'] = self.port
        cfg['external-controller'] = f"127.0.0.1:{self.api_port}"

        # 保存运行时配置
        with open(self.runtime_config, 'w', encoding='utf-8') as f:
            yaml.safe_dump(cfg, f, allow_unicode=True)
        print(f"[Clash] Config ready: {self.runtime_config}")

    def start(self):
        """启动 Clash 核心进程"""
        if self.process:
            return  # 已经启动

        # 启动 Clash 进程（后台运行，无窗口）
        cmd = [self.executable, "-f", self.runtime_config]
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )

        # 等待 Clash API 就绪（最多 10 秒）
        for _ in range(10):
            try:
                requests.get(self.api_url, timeout=1)
                print("[Clash] Started")
                return
            except:
                time.sleep(1)

        print("[Clash] Start failed")
        self.stop()

    def stop(self):
        """停止 Clash 核心进程"""
        if self.process:
            self.process.terminate()
            self.process = None

    def get_proxies(self):
        """获取所有代理节点信息"""
        try:
            url = f"{self.api_url}/proxies"
            res = requests.get(url, timeout=5).json()
            return res['proxies']
        except:
            return {}

    def test_latency(self, proxy_name, timeout=5000):
        """
        测试节点延迟
        参数：proxy_name - 节点名称，timeout - 超时时间（毫秒）
        返回：延迟（毫秒），-1 表示测试失败
        """
        try:
            encoded_name = urllib.parse.quote(proxy_name)
            url = f"{self.api_url}/proxies/{encoded_name}/delay?timeout={timeout}&url=http://www.gstatic.com/generate_204"
            res = requests.get(url, timeout=6)
            if res.status_code == 200:
                return res.json().get('delay', 0)
            return -1
        except:
            return -1

    def select_proxy(self, group_name, proxy_name):
        """
        切换到指定节点
        参数：group_name - 代理组名称，proxy_name - 节点名称
        返回：True=切换成功，False=切换失败
        """
        try:
            encoded_group = urllib.parse.quote(group_name)
            url = f"{self.api_url}/proxies/{encoded_group}"
            requests.put(url, json={"name": proxy_name}, timeout=5)
            print(f"[Clash] Switch: {proxy_name}")
            return True
        except:
            return False

    def find_healthy_node(self, group_name=None):
        """
        查找可用的健康节点（延迟低且未被 Google 封禁）
        参数：group_name - 代理组名称（可选，自动查找第一个 Selector 组）
        返回：节点名称，None 表示未找到
        """
        print("[Clash] Finding healthy node...")
        proxies = self.get_proxies()

        # 如果未指定组名，自动查找第一个 Selector 类型的代理组
        if not group_name or group_name not in proxies:
            for key, val in proxies.items():
                if val['type'] == 'Selector' and len(val.get('all', [])) > 0:
                    group_name = key
                    break

        if not group_name or group_name not in proxies:
            return None

        # 获取所有节点并随机打乱顺序
        all_nodes = proxies[group_name]['all']
        random.shuffle(all_nodes)

        # 跳过特殊节点（自动选择、故障转移等）
        skip_keywords = ["自动选择", "故障转移", "DIRECT", "REJECT", "剩余", "到期", "官网"]

        # 逐个测试节点
        for node in all_nodes:
            if any(kw in node for kw in skip_keywords):
                continue

            # 测试延迟
            delay = self.test_latency(node)
            if delay > 0:
                self.select_proxy(group_name, node)

                # 测试是否能访问 Google（检查是否被封禁）
                try:
                    time.sleep(1)
                    test_proxies = {
                        "http": f"http://127.0.0.1:{self.port}",
                        "https": f"http://127.0.0.1:{self.port}"
                    }
                    print(f"   Testing [{node}]...", end="")
                    resp = requests.get("https://www.google.com/ncr", proxies=test_proxies, timeout=5)

                    if resp.status_code == 200 and "sorry" not in resp.text and "unusual traffic" not in resp.text:
                        print(" ✅ PASS")
                        return node
                    else:
                        print(" ❌ Blocked")
                except:
                    print(" ❌ Timeout")

        print("[Clash] No healthy node found")
        return None

# 全局单例实例
_manager_instance = None

def get_manager():
    """
    获取 ClashManager 单例实例
    返回：ClashManager 实例
    """
    global _manager_instance
    if not _manager_instance:
        _manager_instance = ClashManager()
    return _manager_instance

@atexit.register
def cleanup():
    """程序退出时自动清理 Clash 进程"""
    if _manager_instance:
        _manager_instance.stop()
