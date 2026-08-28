import requests


def send_discord(webhook_url, message):
    if not webhook_url:
        return False
    try:
        response = requests.post(
            webhook_url,
            json={"content": message[:2000]},
            timeout=15,
        )
        return response.status_code in (200, 204)
    except requests.RequestException:
        return False


def send_telegram(bot_token, chat_id, message):
    if not bot_token or not chat_id:
        return False
    url = "https://api.telegram.org/bot{token}/sendMessage".format(token=bot_token)
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": message[:4000]},
            timeout=15,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def notify_watch(domain, new_names, discord_webhook=None, telegram_token=None, telegram_chat_id=None):
    if not new_names:
        return

    lines = ["**CTFR-Reloaded** — nuevos subdominios para `{d}`:".format(d=domain)]
    lines.extend(["- {n}".format(n=name) for name in new_names[:30]])
    if len(new_names) > 30:
        lines.append("... y {n} mas".format(n=len(new_names) - 30))
    message = "\n".join(lines)

    if discord_webhook:
        send_discord(discord_webhook, message.replace("**", "").replace("`", ""))
    if telegram_token and telegram_chat_id:
        send_telegram(telegram_token, telegram_chat_id, message)
