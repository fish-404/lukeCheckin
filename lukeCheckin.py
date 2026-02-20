import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 从环境变量读取账号密码（GitHub Actions 用 Secrets，本地可直接赋值）
EMAIL = os.getenv("LUKE_EMAIL") or "你的邮箱"
PWD = os.getenv("LUKE_PASSWORD") or "你的密码"

def auto_checkin():
    """每次重新登录，完成签到"""
    # 浏览器配置（适配本地/GitHub Actions）
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # 无头模式
    chrome_options.add_argument("--no-sandbox")    # Linux 适配
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    # 模拟真人 User-Agent
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)
    try:
        print("🔍 开始登录流程...")
        # 1. 访问登录页面
        driver.get("https://www.lukeacademy.com/auth/signin")
        # 等待输入框加载（延长到15秒，适配慢加载）
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        time.sleep(random.uniform(0.5, 1.0))  # 随机延迟，模拟真人

        # 2. 输入邮箱（适配不同定位方式，按需修改）
        email_input = driver.find_element(By.NAME, "email")
        # 若name找不到，替换为：
        # email_input = driver.find_element(By.XPATH, '//input[@placeholder="邮箱/Email"]')
        email_input.clear()
        email_input.send_keys(EMAIL)
        time.sleep(random.uniform(0.3, 0.8))  # 输入后延迟

        # 3. 输入密码
        pwd_input = driver.find_element(By.NAME, "password")
        # 若name找不到，替换为：
        # pwd_input = driver.find_element(By.XPATH, '//input[@placeholder="密码/Password"]')
        pwd_input.clear()
        pwd_input.send_keys(PWD)
        time.sleep(random.uniform(0.5, 1.2))  # 输入后延迟

        # 4. 点击登录按钮
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "登录") or contains(text(), "Login")]'))
        )
        login_btn.click()
        print("✅ 点击登录按钮，等待跳转...")
        time.sleep(random.uniform(2.0, 3.0))  # 等待登录跳转

        # 5. 访问签到页面
        driver.get("https://www.lukeacademy.com/shop")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(random.uniform(0.5, 1.0))

        # 6. 点击签到按钮
        try:
            checkin_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "签到") or contains(text(), "Checkin")]'))
            )
            checkin_btn.click()
            print("✅ 点击签到按钮成功！")
            time.sleep(2)
            # 验证签到结果
            if "签到成功" in driver.page_source or "已签到" in driver.page_source:
                print("✅ 最终结果：签到成功/今日已签到！")
            else:
                print("ℹ️  签到操作完成，页面无明确提示（大概率成功）")
        except Exception as e:
            print(f"⚠️  未找到签到按钮或已完成签到，报错：{str(e)}")

    except Exception as e:
        print(f"❌ 自动化流程失败：{str(e)}")
    finally:
        # 确保浏览器关闭
        driver.quit()
        print("🔚 浏览器已关闭，流程结束")

if __name__ == "__main__":
    print("===== Luke Academy 自动签到开始 =====")
    auto_checkin()
    print("===== Luke Academy 自动签到结束 =====")