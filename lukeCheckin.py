import os
import time
import random
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests

load_dotenv()

# 从环境变量读取账号密码（GitHub Actions 用 Secrets，本地可直接赋值）
EMAIL = os.getenv("LUKE_EMAIL") 
PWD = os.getenv("LUKE_PASSWORD") 
WEWORK_ROBOT_WEBHOOK = os.getenv("WEWORK_ROBOT_WEBHOOK")

def get_chrome_driver(chrome_options):
    # 判断是否为 GitHub Actions 环境（通过环境变量标识）
    is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
    print('🔍 当前环境：', 'GitHub Actions' if is_github_actions else '本地')
    if is_github_actions:
        # GitHub Actions 环境：用 webdriver_manager 解决版本匹配
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    else:
        # 本地环境：原生快速初始化（无 Service）
        return webdriver.Chrome(options=chrome_options)

def send_wechat_notify(title, content):
    if not WEWORK_ROBOT_WEBHOOK:
        print("⚠️  未配置企业微信机器人Webhook，跳过推送")
        return
    try:
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "content": f"# {title}\n{content}\n\n**消息时间**：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
            }
        }
        requests.post(WEWORK_ROBOT_WEBHOOK, json=data, timeout=10)
        print("✅ 企业微信机器人推送成功！")
    except Exception as e:
        print(f"❌ 企业微信机器人推送失败：{str(e)}")

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
    driver = None

    try:
        print("🔧 开始初始化Chrome浏览器...")
        driver = get_chrome_driver(chrome_options)
        print("🔍 开始登录流程...")
        # 1. 访问登录页面
        driver.get("https://www.lukeacademy.com/auth/signin")
        # 等待输入框加载（延长到15秒，适配慢加载）
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//input[@type="email"]'))
        )
        time.sleep(random.uniform(0.5, 1.0))  # 随机延迟，模拟真人

        # 2. 填写邮箱
        email_input = driver.find_element(By.XPATH, '//input[@type="email"]')
        email_input.clear()
        email_input.send_keys(EMAIL)
        time.sleep(random.uniform(0.3, 0.8))  # 输入后延迟

        # 3. 填写密码
        pwd_input = driver.find_element(By.XPATH, '//input[@type="password"]')
        pwd_input.clear()
        pwd_input.send_keys(PWD)
        time.sleep(random.uniform(0.5, 1.2))  # 输入后延迟

        # 4. 点击登录按钮
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]'))
        )
        login_btn.click()
        print("✅ 点击登录按钮，等待跳转...")
        time.sleep(random.uniform(2.0, 3.0))  # 等待登录跳转

        # 5. 访问签到页面
        driver.get("https://www.lukeacademy.com/shop")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(random.uniform(1.0, 2.0))

        # 6. 点击签到按钮
        try:
            checkin_btn = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//button[contains(., "每日签到")]'))  # 等待元素可见
            )
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            actions.move_to_element(checkin_btn).click().perform()

            print("✅ 点击签到按钮成功！")
            time.sleep(2)
            # 验证签到结果
            if "已签到" in driver.page_source:
                print("✅ 最终结果：签到成功/今日已签到！")
                score_num = driver.find_element(
                    By.XPATH,
                    '//a[contains(@href, "/shop#credits-exchange")]//span[@title]'
                ).get_attribute("title")
                send_wechat_notify("签到成功", f"今日已签到，当前积分数：{score_num}")
                print(f"🎉 当前积分数：{score_num}")
        except Exception as e:
            print(f"⚠️  未找到签到按钮或已完成签到，报错：{str(e)}")
            send_wechat_notify("签到失败", str(e))

    except Exception as e:
        print(f"❌ 自动化流程失败：{str(e)}")
        send_wechat_notify("自动签到失败", str(e))
    finally:
        # 确保浏览器关闭
        driver.quit()
        print("🔚 浏览器已关闭，流程结束")

if __name__ == "__main__":
    print("===== Luke Academy 自动签到开始 =====")
    auto_checkin()
    print("===== Luke Academy 自动签到结束 =====")