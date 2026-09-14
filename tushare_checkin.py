import os
import json
import requests

url = "https://tushare.pro/wctapi/user_center/sign"

cookie = os.getenv("TUSHARE_COOKIE")

if not cookie:
    raise RuntimeError("未设置 TUSHARE_COOKIE")

headers = {
    "Cookie": cookie,
    "Origin": "https://tushare.pro",
    "Referer": "https://tushare.pro/weborder/",
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
}

try:
    r = requests.post(url, headers=headers, timeout=20)

    print("HTTP状态码:", r.status_code)
    print("服务器返回:", r.text)

    r.raise_for_status()

    data = r.json()

    # Tushare 接口 code=0 表示请求正常
    if data.get("code") != 0:
        raise RuntimeError(f"接口返回异常: {data}")

    result = data.get("data", {})
    success = result.get("success")
    message = result.get("message", "")

    print("签到结果:", message)

    # 已签到也视为正常
    if success is True:
        print("✅ 签到成功")
    elif "已达上限" in message or "已完成" in message:
        print("ℹ️ 今日已经签到，无需重复签到")
    else:
        raise RuntimeError(f"签到未成功: {message}")

except requests.RequestException as e:
    print("❌ 网络请求失败:", e)
    raise
except (ValueError, json.JSONDecodeError) as e:
    print("❌ 返回内容不是有效 JSON:", e)
    raise
