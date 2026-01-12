# Gemini Business 自动注册工具 - 使用说明

## 项目简介

基于 DrissionPage 的 Gemini Business 自动注册工具，使用临时邮箱和外部代理实现全自动注册流程。

**致谢**：邮箱注册功能来自 [DuckMail](https://linux.do/u/syferie/summary)
注册成功后的登录地址：https://business.gemini.google/ 邮件登录地址：https://ducktempmail.netlify.app/

## 功能特性

- ✅ **浏览器自动化**：基于 DrissionPage 的 Chromium 自动化
- ✅ **外部代理支持**：使用 Clash Verge 等外部代理工具
- ✅ **临时邮箱**：通过 DuckMail API 自动生成临时邮箱
- ✅ **自动验证**：自动获取并填入邮箱验证码
- ✅ **循环注册**：支持批量自动注册

## 环境要求

- **操作系统**：Windows 10/11
- **Python**：3.10 或更高版本
- **浏览器**：Chrome/Chromium（系统已安装）
- **代理工具**：Clash Verge Rev（推荐）

## 项目结构

```
e:\v1.0.0.Gemini.Business\
├── auto_register_browser.py   # 主自动化脚本
├── mail_client.py              # 临时邮箱客户端
├── clash_manager.py            # Clash 代理管理器（保留但不使用）
├── requirements.txt            # Python 依赖
├── Run.bat                     # 快速启动脚本
├── 一键配置环境.bat             # 环境配置脚本
├── 使用说明.md                  # 本文档
├── README.md                   # 原项目说明
└── venv/                       # Python 虚拟环境（自动生成）

运行时自动生成的文件：
├── result.csv                  # 注册成功的账号
└── log.txt                     # 运行日志
```

---

## 快速开始

### 第一步：配置 Python 环境

1. **运行环境配置脚本**
   ```
   双击运行：一键配置环境.bat
   ```

2. **等待安装完成**
   - 脚本会自动创建虚拟环境
   - 自动安装所有 Python 依赖包
   - 如果清华源失败，会自动切换到阿里云源

3. **验证安装**
   - 看到 "Setup complete!" 表示成功
   - 所有依赖包已安装在 `venv` 虚拟环境中

### 第二步：配置外部代理

#### 2.1 下载 Clash Verge Rev

**下载地址**：
- GitHub: https://github.com/clash-verge-rev/clash-verge-rev/releases
- 选择最新版本的 `Clash.Verge_xxx_x64-setup.exe`

#### 2.2 安装并启动

1. 双击安装程序完成安装
2. 启动 Clash Verge Rev

#### 2.3 导入代理订阅

1. 在 Clash Verge 中点击 **订阅** 或 **Profiles**
2. 点击 **新建** → **从链接导入**
3. 粘贴你的 Clash 订阅链接
4. 点击 **导入** 并等待更新完成

**示例订阅链接**：
```
https://your-subscription-url
```

#### 2.4 启用代理

1. 在主界面打开 **系统代理** 开关
2. 选择 **规则模式** 或 **Rule**
3. 在 **代理** 标签中选择一个可用节点
4. 点击 **延迟测试** 确认节点可用

#### 2.5 确认端口设置

1. 打开 **设置** → 查看 **混合端口**
2. 确认端口为 **7890**（默认值）
3. 如果端口不同，需要修改配置（见下方说明）

### 第三步：运行程序

1. **确保 Clash Verge 正在运行**
   - 系统代理已启用
   - 已选择可用节点

2. **启动注册程序**
   ```
   双击运行：Run.bat
   ```

3. **观察运行过程**
   - 程序会自动注册临时邮箱
   - 启动浏览器访问 Gemini Business
   - 自动填写邮箱并获取验证码
   - 完成注册并保存账号

4. **查看注册结果**
   - 成功的账号保存在 `result.csv`
   - 运行日志保存在 `log.txt`

### 第四步：登陆使用

1. **Business 登录地址**
   - https://business.gemini.google/  使用`result.csv`中的Account登陆，等第2步的验证码正常登陆
2. **账号信息登陆**
   - https://ducktempmail.netlify.app/ 使用`result.csv`中的Account和Password登陆邮箱管理，用于接收gemini的验证码

## 配置说明

### 代理端口配置

如果你的代理工具使用不同的端口，需要修改以下文件：

**修改 `auto_register_browser.py`**（第 17 行）：
```python
PROXY_ADDR = "127.0.0.1:7890"  # 改为你的代理端口
```

**修改 `mail_client.py`**（第 8 行）：
```python
PROXY_URL = "http://127.0.0.1:7890"  # 改为你的代理端口
```

### 常用代理端口

| 工具 | 默认端口 |
|------|---------|
| Clash Verge | 7890 |
| Clash for Windows | 7890 |
| v2rayN | 10808 |

### 注册间隔调整

修改 `auto_register_browser.py`（第 234 行）：
```python
time.sleep(3)  # 改为你想要的间隔秒数
```

---

## 输出文件

### result.csv
注册成功的账号列表：

| ID | Account | Password | Date |
|----|---------|----------|------|
| 1 | temp_xxx@duck.com | Pwdxxx | 2026-01-12 |

### log.txt
详细的运行日志，包含：
- 代理连接状态
- 邮箱注册信息
- 浏览器操作步骤
- 错误信息（如有）

---

## 常见问题

### Q1: 提示 "代理连接失败"
**解决方案**：
1. 确认 Clash Verge 正在运行
2. 确认系统代理已启用
3. 检查端口设置是否正确（默认 7890）
4. 尝试切换不同的代理节点

### Q2: 邮箱注册失败
**解决方案**：
1. 检查代理是否正常工作
2. 测试访问：https://api.duckmail.sbs/domains
3. 如果 DuckMail API 不可用，等待服务恢复

### Q3: 浏览器无法打开或加载缓慢
**解决方案**：
1. 检查代理节点延迟（建议 < 300ms）
2. 切换到延迟更低的节点
3. 确认 Chrome 浏览器已正确安装

### Q4: Google 提示 "检测到异常流量"
**解决方案**：
1. 切换到不同的代理节点
2. 使用住宅 IP 节点（如果有）
3. 增加注册间隔时间
4. 降低注册频率

### Q5: 验证码获取超时
**解决方案**：
1. 检查邮箱 API 连接是否正常
2. 等待时间默认 180 秒，通常足够
3. 如果经常超时，检查网络连接

---

## 已知问题

| 问题 | 说明 | 影响 |
|------|------|------|
| **IP 封锁** | 部分代理节点被 Google 封禁 | 切换到其他节点即可 |
| **按钮匹配不正确** | 有概率触发点击验证和重发验证码两个按钮 | 不影响功能，程序会自动处理 |
| **页面加载慢** | 网络不稳定时页面加载较慢 | 可能导致超时，建议使用低延迟节点 |
| **纯 API 注册** | Google 使用 reCAPTCHA Enterprise | 无法绕过，必须使用浏览器自动化 |

**注意**：这些问题是正常现象，不影响程序的基本功能。

---

## 验证代理连接

### 方法 1: 浏览器测试
1. 在浏览器中设置代理为 `127.0.0.1:7890`
2. 访问 https://www.google.com
3. 能正常访问说明代理工作正常

### 方法 2: 命令行测试
```powershell
# 测试端口是否开放
Test-NetConnection -ComputerName 127.0.0.1 -Port 7890

# 使用 curl 测试
curl -x http://127.0.0.1:7890 https://www.google.com
```

### 方法 3: Python 测试
```python
import requests

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

try:
    response = requests.get("https://www.google.com", proxies=proxies, timeout=10)
    print("✅ 代理连接成功！")
except Exception as e:
    print(f"❌ 代理连接失败: {e}")
```

---

## 工作流程

```
1. 启动 Clash Verge → 启用系统代理
2. 运行 Run.bat → 激活虚拟环境
3. 检测外部代理 → 连接到 127.0.0.1:7890
4. 注册临时邮箱 → 通过 DuckMail API
5. 启动浏览器 → 访问 Gemini Business
6. 输入邮箱 → 点击继续
7. 等待验证码 → 自动获取并填入
8. 完成注册 → 保存到 result.csv
9. 循环执行 → 间隔 3 秒
```

---

## 注意事项

1. **代理必须正常工作**
   - 程序依赖外部代理访问 Google 和邮箱 API
   - 启动程序前务必确认代理已启用

2. **节点选择**
   - 选择延迟低、稳定的节点
   - 避免使用被 Google 封禁的节点
   - 建议定期切换节点

3. **注册频率**
   - 不要过于频繁注册（建议间隔 ≥ 3 秒）
   - 避免短时间内大量注册
   - 注意 IP 可能被临时限制

4. **账号安全**
   - 注册的账号保存在 `result.csv`
   - 请妥善保管账号信息
   - 定期备份重要数据

---

## 依赖项

程序使用以下 Python 包（已自动安装）：

- **DrissionPage** >= 4.1.0 - 浏览器自动化
- **requests** >= 2.31.0 - HTTP 请求
- **PyYAML** >= 6.0 - YAML 配置解析

---

## 免责声明

**重要提示：请在使用本工具前仔细阅读以下声明**

1. **学习研究用途**：本项目仅供学习、研究和技术交流使用。

2. **使用者责任**：使用本工具所产生的一切后果由使用者自行承担。

3. **合规使用**：使用者应遵守所在国家/地区的法律法规，以及 Google 服务条款。

4. **无担保声明**：本项目按"现状"提供，不提供任何明示或暗示的担保。

5. **禁止商业用途**：禁止将本工具用于商业目的或大规模滥用。

6. **第三方服务**：本项目依赖第三方服务（DuckMail API、Clash 等），其可用性和稳定性不在作者控制范围内。

7. **随时停止维护**：作者保留随时停止维护本项目的权利，恕不另行通知。

**继续使用本工具即表示您已阅读、理解并同意以上所有条款。**

---

## 许可证

MIT License

---

## 技术支持

如遇到问题，请检查：
1. 本文档的"常见问题"部分
2. `log.txt` 日志文件中的错误信息
3. 确认所有配置步骤都已正确完成

## 项目来源
- **GitHub**: https://github.com/gagmeng/Gemini-Business
- **Forked from GitHub**: https://github.com/Zooo-1/Gemini-Business
- **克隆命令**:
  ```bash
  git clone https://github.com/gagmeng/Gemini-Business.git
  cd Gemini-Business
  ```

---

**祝使用愉快！**
