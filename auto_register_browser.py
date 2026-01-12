# -*- coding: utf-8 -*-
"""
Gemini Business 自动注册工具 - 主程序
功能：使用临时邮箱和外部代理自动注册 Gemini Business 账号
"""

import time
import random
import csv
import os
import sys
from datetime import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
from mail_client import DuckMailClient

# 配置项：是否使用外部代理（True=使用 Clash Verge 等外部工具，False=使用内置 Clash 管理器）
USE_EXTERNAL_PROXY = True

if not USE_EXTERNAL_PROXY:
    from clash_manager import get_manager

# 文件路径配置
CSV_FILE = "result.csv"  # 保存成功注册的账号
LOG_FILE = "log.txt"     # 运行日志文件
PROXY_ADDR = "127.0.0.1:7890"  # 代理地址（Clash Verge 默认端口）

def log(msg, level="INFO"):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    log_line = f"[{timestamp}] [{level}] {msg}"
    print(msg)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_line + '\n')
    except:
        pass

def log_step(step_name, start_time, success=True):
    """记录步骤执行时间（性能日志）"""
    elapsed = (time.time() - start_time) * 1000
    status = "OK" if success else "FAIL"
    log(f"  [{status}] {step_name}: {elapsed:.0f}ms", "PERF")

def get_random_ua():
    """生成随机 User-Agent，模拟不同版本的 Chrome 浏览器"""
    versions = ["120.0.0.0", "121.0.0.0", "122.0.0.0", "123.0.0.0", "124.0.0.0"]
    v = random.choice(versions)
    return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v} Safari/537.36"

def get_next_id():
    """获取下一个账号 ID（从 CSV 文件中读取最后一个 ID + 1）"""
    if not os.path.exists(CSV_FILE):
        return 1
    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
            lines = list(csv.reader(f))
            if len(lines) <= 1: return 1
            last_row = lines[-1]
            if last_row and last_row[0].isdigit():
                return int(last_row[0]) + 1
    except:
        pass
    return 1

def save_account(email, password):
    """保存成功注册的账号到 CSV 文件"""
    file_exists = os.path.exists(CSV_FILE)
    next_id = get_next_id()
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(CSV_FILE, 'a', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['ID', 'Account', 'Password', 'Date'])
            writer.writerow([next_id, email, password, date_str])
        log(f"[Save] {email}")
    except Exception as e:
        log(f"[Error] Save failed: {e}", "ERROR")

def run_browser_cycle():
    """执行一次完整的注册流程"""
    # 步骤1: 检查代理设置
    if not USE_EXTERNAL_PROXY:
        # 使用内置 Clash 管理器
        clash = get_manager()
        clash.start()

        node = clash.find_healthy_node()
        if not node:
            log("[Clash] No healthy node")
            time.sleep(5)
            return True
    else:
        # 使用外部代理（Clash Verge 等）
        log("[Proxy] Using external proxy at " + PROXY_ADDR)

    # 步骤2: 注册临时邮箱
    mail = DuckMailClient()
    print("-" * 40)
    if not mail.register():
        log("[Mail] Register failed")
        return True

    log(f"[Mail] {mail.email}")

    # 步骤3: 配置浏览器选项
    co = ChromiumOptions()
    co.set_argument('--incognito')  # 无痕模式
    co.set_argument(f'--proxy-server=http://{PROXY_ADDR}')  # 设置代理
    co.set_user_agent(get_random_ua())  # 随机 UA
    co.set_argument('--disable-blink-features=AutomationControlled')  # 隐藏自动化特征
    co.auto_port()  # 自动分配端口

    page = None
    try:
        # 步骤4: 启动浏览器
        log("[Browser] Starting...")
        page = ChromiumPage(co)
        page.run_js("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # 隐藏 webdriver 属性

        # 步骤5: 访问 Gemini Business 页面
        t = time.time()
        page.get("https://business.gemini.google/", timeout=30)
        time.sleep(3)
        log_step("Load page", t)

        # 步骤6: 查找邮箱输入框
        t = time.time()
        email_input = page.ele('#email-input', timeout=3) or \
                      page.ele('css:input[name="loginHint"]', timeout=2) or \
                      page.ele('css:input[type="text"]', timeout=2)
        if not email_input:
            log("[Error] Email input not found", "ERROR")
            return True
        log_step("Find email input", t)

        # 步骤7: 输入邮箱地址
        t = time.time()
        email_input.click()
        time.sleep(0.3)
        email_input.clear()
        time.sleep(0.2)
        email_input.input(mail.email)
        time.sleep(0.3)
        # 触发输入事件，确保页面识别到输入
        page.run_js('''
            let el = document.querySelector("#email-input");
            if(el) {
                el.dispatchEvent(new Event("input", {bubbles: true}));
                el.dispatchEvent(new Event("change", {bubbles: true}));
                el.dispatchEvent(new Event("blur", {bubbles: true}));
            }
        ''')
        log_step("Input email", t)

        # 步骤8: 点击继续按钮
        t = time.time()
        time.sleep(0.5)
        continue_btn = page.ele('tag:button@text():使用邮箱继续', timeout=2) or \
                       page.ele('tag:button', timeout=1)
        if continue_btn:
            try:
                continue_btn.click()
            except:
                continue_btn.click(by_js=True)  # 如果普通点击失败，使用 JS 点击
            log_step("Click continue", t)
        else:
            email_input.input('\n')  # 如果找不到按钮，尝试按回车
            log_step("Press enter", t)

        time.sleep(3)

        # 步骤9: 等待验证码输入框出现
        t = time.time()
        code_input = None
        for _ in range(10):
            code_input = page.ele('css:input[name="pinInput"]', timeout=2) or \
                         page.ele('css:input[type="tel"]', timeout=1)
            if code_input:
                break
            time.sleep(0.5)

        if not code_input:
            log("[Error] Code input not found", "ERROR")
            return True
        log_step("Find code input", t)

        # 步骤10: 从邮箱获取验证码（最多等待 180 秒）
        t = time.time()
        code = mail.wait_for_code(timeout=180)
        if not code:
            log("[Error] Code timeout", "ERROR")
            return True
        log_step(f"Get code {code}", t)

        # 步骤11: 输入验证码
        t = time.time()
        code_input = page.ele('css:input[name="pinInput"]', timeout=3) or \
                     page.ele('css:input[type="tel"]', timeout=2)
        if not code_input:
            log("[Error] Code input expired", "ERROR")
            return True

        code_input.click()
        time.sleep(0.2)
        code_input.input(code)
        time.sleep(0.3)
        # 触发输入事件
        try:
            page.run_js('''
                let el = document.querySelector("input[name=pinInput]") || document.querySelector("input[type=tel]");
                if(el) {
                    el.dispatchEvent(new Event("input", {bubbles: true}));
                    el.dispatchEvent(new Event("change", {bubbles: true}));
                }
            ''')
        except:
            pass
        log_step("Input code", t)

        # 步骤12: 查找并点击验证按钮
        t = time.time()
        verify_btn = None
        buttons = page.eles('tag:button')
        for btn in buttons:
            btn_text = btn.text.strip() if btn.text else ""
            # 排除"重新发送"等按钮，找到真正的验证按钮
            if btn_text and "重新" not in btn_text and "发送" not in btn_text and "resend" not in btn_text.lower():
                verify_btn = btn
                break

        if verify_btn:
            try:
                verify_btn.click()
            except:
                verify_btn.click(by_js=True)
            log_step("Click verify", t)
        else:
            code_input.input('\n')  # 如果找不到按钮，尝试按回车
            log_step("Press enter", t, success=False)

        # 步骤13: 等待页面跳转，判断注册是否成功
        for _ in range(5):
            time.sleep(3)
            curr_url = page.url
            # 如果 URL 包含这些关键词，说明注册成功
            if any(kw in curr_url for kw in ["home", "admin", "setup", "create", "dashboard"]):
                break

        curr_url = page.url
        fail_keywords = ["verify", "oob", "error"]

        # 判断注册结果
        if any(kw in curr_url for kw in fail_keywords):
            log("❌ Failed")
        else:
            log("✅ Success")
            save_account(mail.email, mail.password)

    except Exception as e:
        log(f"[Exception] {e}", "ERROR")
    finally:
        # 清理：关闭浏览器
        if page:
            page.quit()
        log("[Browser] Closed")

    return True

if __name__ == "__main__":
    """主程序入口：循环执行注册流程"""
    print("Starting... (Ctrl+C to stop)")
    try:
        while True:
            run_browser_cycle()  # 执行一次注册
            print("\nCooldown 3s...")
            time.sleep(3)  # 冷却 3 秒后继续下一次
    except KeyboardInterrupt:
        pass  # 用户按 Ctrl+C 停止程序
