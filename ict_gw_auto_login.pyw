from selenium import webdriver
import schedule
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time
import sys
import os
from datetime import datetime
import requests
import random
import subprocess
import argparse
from functools import partial
import ctypes

def hide_console():
    ctypes.windll.kernel32.FreeConsole()

userName = "yourAccount"
passWord = "yourPswd"


# 获取当前脚本所在路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 相对路径：日志文件保存在当前脚本所在目录
log_file_path = os.path.join(current_dir, 'log.txt')

# 最大行数限制
MAX_LINES = 200

# 函数：检查并确保日志文件行数不超过 MAX_LINES
def manage_log_file():
    with open(log_file_path, 'r+', encoding='utf-8') as file:
        lines = file.readlines()  # 读取所有行
        # 如果行数超过 MAX_LINES，删除多余的行
        if len(lines) > MAX_LINES:
            file.seek(0)  # 移动到文件开头
            file.writelines(lines[:MAX_LINES])  # 仅保留前 MAX_LINES 行
            file.truncate()  # 截断文件，删除多余的内容

# 函数：将输出写入日志文件开头
def log_to_file(message):
    # 获取当前时间
    current_time = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    log_message = f"{current_time} {message}\n"

    # 打开文件，追加到文件开头
    with open(log_file_path, 'r+', encoding='utf-8') as file:
        # 读取现有内容
        existing_content = file.read()
        # 将新消息写到文件开头
        file.seek(0)
        file.write(log_message + existing_content)

    # 确保文件行数不超过最大限制
    manage_log_file()

# 重定向 sys.stdout 到 log_to_file 函数
sys.stdout = open(log_file_path, 'a', encoding='utf-8')  # 追加模式打开文件

# 网络连接检查函数
def check_connection_with_curl(test_urls=None):
    if test_urls is None:
        test_urls = ["baidu.com"]  # 默认测试网址
    max_retries = 3  # 对每个 URL 进行最多 5 次尝试
    retry_interval_min = 1.0  # 每次尝试的最短间隔（秒）
    retry_interval_max = 2.0  # 每次尝试的最长间隔（秒）

    for url in test_urls:
        consecutive_failures = 0  # 当前 URL 连续失败的次数

        for _ in range(max_retries):
            try:
                # 使用 curl 获取网页内容，并检查是否包含 "baidu.com"
                result = subprocess.run(['curl', url], capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW)
                if 'baidu.com' in result.stdout:
                    log_to_file(f"成功连接到 {url}，且网页内容包含 'baidu.com'。")
                    return True  # 如果成功连接到此 URL，认为网络连接正常，直接返回
                else:
                    log_to_file(f"第 {consecutive_failures + 1} 次连接到 {url} 失败，或网页内容不包含 'baidu.com'。")
                    log_to_file(f"result.stdout的内容：\n{result.stdout}")
            except subprocess.TimeoutExpired:
                log_to_file(f"连接到 {url} 超时。")
            except subprocess.CalledProcessError as e:
                log_to_file(f"尝试连接 {url} 时发生错误: {e}")

            # 增加失败计数
            consecutive_failures += 1
            # 如果连续 5 次失败，则认为此 URL 不可连接
            if consecutive_failures >= max_retries:
                log_to_file(f"{url} 连续 {max_retries} 次连接失败，认为此 URL 无法连接。")
                break

            # 随机等待 1.0 到 2.0 秒，模拟间隔
            time.sleep(random.uniform(retry_interval_min, retry_interval_max))

    # 如果所有 URL 都无法连接，返回 False
    return False

# 登录流程
def login(userName, passWord):
    log_to_file(f"无法连接到网络，开始执行登录流程...")

    driver = webdriver.Edge()  # 启动浏览器

    try:
        # 打开登录页面
        driver.get("https://the_url_of_gw")  # 替换为实际的目标网址
        time.sleep(3)  # 等待页面加载

        # 定位并填写用户名
        username = driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入账号']")
        username.send_keys(userName)  # 替换为你的用户名
        time.sleep(0.2)

        # 定位并填写密码
        password = driver.find_element(By.CSS_SELECTOR, "input[placeholder='请输入密码']")
        password.send_keys(passWord)  # 替换为你的密码
        time.sleep(0.2)

        # 点击登录按钮
        login_button = driver.find_element(By.CSS_SELECTOR, """button[id="login-account"]""")
        login_button.click()
        log_to_file(f"登录流程已完成，等待页面加载...")
        time.sleep(2)  # 等待登录完成
    except NoSuchElementException as e:
        log_to_file(f"登录流程出错，元素未找到：{e}")
    except WebDriverException as e:
        log_to_file(f"WebDriver 出错：{e}")
    finally:
        driver.quit()


def task1():
    login(userName, passWord)

def task2():
    # 检查网络连接
    if not check_connection_with_curl():
        # 如果无法连接，运行登录流程
        login(userName, passWord)
        # 登录完成后再次检查网络连接
        if check_connection_with_curl():
            log_to_file(f"登录完成后，网络连接已恢复！")
        else:
            log_to_file(f"登录完成后，仍然无法连接到网络，请检查登录信息或网络配置。")
    else:
        log_to_file(f"网络连接正常，无需登录。")


# 主程序逻辑
if __name__ == "__main__":
    hide_console()
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="网络连接与登录工具")
    parser.add_argument("--connect-only", action="store_true", help="不检查网络连接，仅执行登录")
    args = parser.parse_args()

    if args.connect_only:
        schedule.every(1).minutes.do(task1)
    else:
        schedule.every(1).minutes.do(task2)

    # 持续运行，定期检查并执行任务
    while True:
        schedule.run_pending()  # 执行所有待处理的任务
        time.sleep(1)  # 每次循环等待1秒