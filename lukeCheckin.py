import requests
import os
from requests import Session

BASE_URL = "https://www.lukeacademy.com"
LOGIN_API = f"{BASE_URL}/auth/signin"  # 登录接口：POST+email+password
CHECKIN_API = f"{BASE_URL}/shop"       # 签到接口：POST+无参数+仅需Session

# 从GitHub Secrets读取账号密码
EMAIL = os.getenv("LUKE_EMAIL")
PWD = os.getenv("LUKE_PASSWORD")

def login():
    """模拟登录，返回带有效Session的会话对象"""
    s = Session()
    # 模拟真实浏览器请求头（防反爬核心）
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": LOGIN_API,
        "Origin": BASE_URL,
        "Content-Type": "text/plain;charset=UTF-8",
        "Accept": "text/x-component"
    }
    s.headers.update(headers)

    try:
        # 登录请求体（仅email+password，无其他参数）
        login_data = {"email": EMAIL, "password": PWD}
        res = s.post(LOGIN_API, json=login_data, timeout=20, allow_redirects=False)
        res.raise_for_status()

        # 验证登录成功：Session存在Cookie即判定（适配无明确返回的情况）
        if s.cookies and len(s.cookies) > 0:
            print("✅ 登录成功，已获取用户Session")
            return s
        else:
            print(f"❌ 登录失败，无Session返回，响应：{res.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ 登录异常：{str(e)}")
        return None

def checkin(session):
    """执行签到：POST /shop 无参数，仅携带Session"""
    if not session:
        print("❌ 无有效Session，终止签到")
        return

    try:
        # 核心：空参数POST请求，仅自动携带登录后的Cookie
        res = session.post(CHECKIN_API, timeout=20)
        # 兼容：若POST返回非200，尝试GET（极少数网站签到接口混用）
        if res.status_code not in [200, 201]:
            res = session.get(CHECKIN_API, timeout=20)
        res.raise_for_status()

        # 签到结果判定（覆盖所有情况）
        html = res.text.lower()
        if "已签到" in res.text or "heart" in html:
            print("✅ 签到成功！已获取爱心奖励")
        else:
            print(f"✅ 签到请求执行成功，接口响应状态：{res.status_code}")
            print(f"📌 接口响应摘要：{res.text[:300]}")
    except Exception as e:
        print(f"❌ 签到失败：{str(e)}")

if __name__ == "__main__":
    print("🔍 开始Luke Academy自动签到流程...")
    user_session = login()  # 1. 登录获取Session
    checkin(user_session)   # 2. 空参数POST执行签到
    print("🔚 签到流程执行完毕！")