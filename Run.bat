@echo off
REM ========================================
REM Gemini Business 自动注册工具 - 启动脚本
REM 功能：激活虚拟环境并运行主程序
REM 使用前提：
REM   1. 已运行 "一键配置环境.bat" 完成环境配置
REM   2. 已安装并启动 Clash Verge（或其他代理工具）
REM   3. 代理端口为 7890（默认）
REM ========================================

REM 设置控制台编码为 UTF-8（支持中文显示）
chcp 65001 >nul

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 激活 Python 虚拟环境
call venv\Scripts\activate

REM 运行主程序（循环注册 Gemini Business 账号）
REM 按 Ctrl+C 可以停止程序
python auto_register_browser.py

REM 程序结束后暂停，等待用户查看结果
pause
