# Tushare 自动签到

一个基于 GitHub Actions 的 Tushare 每日自动签到脚本。

通过调用 Tushare 个人中心的签到接口：

```text
POST https://tushare.pro/wctapi/user_center/sign
````

实现每日自动签到获取积分。

项目使用 GitHub Actions 定时执行，无需服务器，也不需要本地电脑保持开机。

---

## 功能

* ✅ Tushare 每日自动签到
* ✅ GitHub Actions 定时运行
* ✅ 支持手动运行
* ✅ 自动识别“今日已签到”
* ✅ Cookie 通过 GitHub Secrets 保存
* ✅ 无需 Selenium / Chrome
* ✅ 无需长期运行服务器

---

## 项目结构

```text
tushare-checkin/
├── .github/
│   └── workflows/
│       └── tushare-checkin.yml
├── tushare_checkin.py
└── README.md
```

---

## 使用方法

### 1. Fork 或创建仓库

可以直接 Fork 本仓库，也可以将以下文件复制到自己的 GitHub 仓库：

```text
tushare_checkin.py
.github/workflows/tushare-checkin.yml
```

如果仓库中需要保存自己的配置，请不要直接将 Cookie 写进代码。

---

## 2. 获取 Tushare Cookie

首先登录：

```text
https://tushare.pro
```

进入：

```text
权限中心 → 我的权益
```

然后按：

```text
F12
```

打开浏览器开发者工具。

选择：

```text
Network / 网络
```

刷新页面或点击一次“每日签到”。

找到类似：

```text
sign
tasks
score
```

的请求。

其中签到接口一般为：

```text
https://tushare.pro/wctapi/user_center/sign
```

点击请求后，在：

```text
Request Headers / 请求标头
```

找到：

```text
Cookie
```

复制 Cookie 的完整值。

格式可能类似：

```text
uid=xxxxxxxx; username=xxxxxxxx
```

> 注意：Cookie 属于敏感登录信息，请不要直接写入代码，也不要提交到公开仓库。

---

## 3. 创建 GitHub Secret

进入自己的仓库：

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

创建：

```text
Name:
TUSHARE_COOKIE
```

Value 填写刚才复制的完整 Cookie。

例如：

```text
uid=xxxxxxxx; username=xxxxxxxx
```

只填写 Cookie 的值，不需要写：

```text
Cookie:
```

---

## 4. GitHub Actions 配置

工作流文件：

```text
.github/workflows/tushare-checkin.yml
```

示例：

```yaml
name: Tushare Daily Check-in

on:
  workflow_dispatch:

  schedule:
    # GitHub Actions 使用 UTC
    # UTC 02:00 = 北京时间 10:00
    - cron: '0 2 * * *'

jobs:
  checkin:
    runs-on: ubuntu-latest

    env:
      FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

    steps:
      - name: Checkout repository
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.13'

      - name: Install requests
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run Tushare check-in
        env:
          TUSHARE_COOKIE: ${{ secrets.TUSHARE_COOKIE }}
        run: |
          python tushare_checkin.py
```

默认每天：

```text
北京时间 10:00
```

执行签到。

如果需要修改运行时间，请修改：

```yaml
cron: '0 2 * * *'
```

注意 GitHub Actions 的 cron 使用 UTC 时间。

---

## 5. Python 签到脚本

`tushare_checkin.py`：

```python
import os
import requests

URL = "https://tushare.pro/wctapi/user_center/sign"

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

response = requests.post(
    URL,
    headers=headers,
    timeout=20
)

print("HTTP状态码:", response.status_code)
print("服务器返回:", response.text)

response.raise_for_status()

data = response.json()

if data.get("code") != 0:
    raise RuntimeError(
        f"Tushare 接口返回异常: {data}"
    )

result = data.get("data", {})

success = result.get("success")
message = result.get("message", "")

print("签到结果:", message)

if success is True:
    print("✅ Tushare 签到成功")

elif "已达上限" in message or "已完成" in message:
    print("ℹ️ 今日已经签到，无需重复签到")

else:
    raise RuntimeError(
        f"❌ Tushare 签到失败: {message}"
    )
```

---

## 6. 手动测试

配置 Secret 后，进入：

```text
Actions
→ Tushare Daily Check-in
→ Run workflow
```

手动运行一次。

如果当天已经签到，日志可能显示：

```text
HTTP状态码: 200
签到结果: 今日已完成 1 次，已达上限 1 次
ℹ️ 今日已经签到，无需重复签到
```

这属于正常情况。

如果当天还没有签到，正常情况下会看到类似：

```text
✅ Tushare 签到成功
```

---

## 本地测试

Windows PowerShell：

```powershell
$env:TUSHARE_COOKIE='uid=xxxx; username=xxxx'

python tushare_checkin.py
```

Linux / macOS：

```bash
export TUSHARE_COOKIE='uid=xxxx; username=xxxx'

python tushare_checkin.py
```

---

## Cookie 失效

本项目依赖 Tushare 网页登录 Cookie。

如果 GitHub Actions 出现：

```text
401
403
未登录
未授权
```

或者签到失败，可能是 Cookie 已经过期。

解决方法：

1. 重新登录 Tushare
2. 获取新的 Cookie
3. 更新 GitHub Secret：

```text
TUSHARE_COOKIE
```

不需要修改代码。

---

## 安全提醒

如果仓库是 Public，请务必注意：

* ❌ 不要把 Cookie 写进 `tushare_checkin.py`
* ❌ 不要把 Cookie 写进 `.yml`
* ❌ 不要把 Cookie 放进 `README.md`
* ❌ 不要在 Issue 中公开 Cookie
* ❌ 不要上传包含 Cookie 的截图
* ✅ Cookie 只保存在 GitHub Actions Secrets 中

GitHub Actions 中使用：

```yaml
${{ secrets.TUSHARE_COOKIE }}
```

即可。

---

## 原理

Tushare 个人中心的“每日签到”功能实际上通过一个 XHR 请求完成：

```text
POST /wctapi/user_center/sign
```

请求依赖当前用户的登录 Cookie。

因此，本项目通过：

```text
GitHub Actions
      ↓
读取 TUSHARE_COOKIE
      ↓
发送 POST 请求
      ↓
Tushare 验证登录状态
      ↓
完成每日签到
      ↓
获得积分
```

实现自动签到。

相比 Selenium 浏览器自动化，这种方式资源占用更低，运行速度也更快。

---

## 注意事项

Tushare 官方可能随时调整：

* 登录机制
* Cookie 格式
* API 地址
* 签到规则
* 积分规则

如果接口发生变化，本项目可能需要同步更新。

---

## 免责声明

本项目仅用于学习 GitHub Actions、Python 网络请求和自动化任务。

请合理使用，并遵守 Tushare 平台相关规则。

本项目与 Tushare 官方无关。

因使用本项目产生的任何账号、积分或其他问题，使用者需自行承担相关责任。
