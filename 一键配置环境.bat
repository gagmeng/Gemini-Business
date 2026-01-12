@echo off
REM ========================================
REM Gemini Business 自动注册工具 - 环境配置脚本
REM 功能：自动创建 Python 虚拟环境并安装依赖包
REM ========================================

REM 设置控制台编码为 UTF-8（支持中文显示）
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo  Gemini Business Auto Register - Setup
echo ========================================
echo.

REM ========================================
REM 步骤 1: 检查 Python 是否已安装
REM ========================================
echo [1/4] Checking Python...
python --version
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM ========================================
REM 步骤 2: 创建 Python 虚拟环境
REM ========================================
echo.
echo [2/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo [OK] venv created
) else (
    echo [OK] venv exists
)

REM ========================================
REM 步骤 3: 激活虚拟环境
REM ========================================
echo.
echo [3/4] Activating environment...
call venv\Scripts\activate

REM ========================================
REM 步骤 4: 安装 Python 依赖包
REM ========================================
echo.
echo [4/4] Installing dependencies...

REM 清除所有代理环境变量（避免代理干扰 pip 安装）
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
set NO_PROXY=*

REM 尝试使用清华大学镜像源安装（速度快）
echo Trying Tsinghua mirror...
pip install --proxy="" -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host files.pythonhosted.org

REM 如果清华源失败，自动切换到阿里云镜像源
if errorlevel 1 (
    echo.
    echo [WARNING] Tsinghua mirror failed, switching to Aliyun mirror...
    pip install --proxy="" -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
)

REM ========================================
REM 安装完成
REM ========================================
echo.
echo ========================================
echo  Setup complete!
echo  Run: python auto_register_browser.py
echo ========================================
pause
