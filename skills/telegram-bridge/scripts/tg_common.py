"""Shared helpers for the telegram-bridge scripts (stdlib only)."""
import json, os, re, urllib.parse, urllib.request
from pathlib import Path

STATE = Path(os.environ.get("TG_BRIDGE_DIR", Path.home() / ".telegram-bridge"))
STATE.mkdir(parents=True, exist_ok=True)


def _read_env_file(path):
    try:
        for line in Path(path).read_text().splitlines():
            m = re.match(r"\s*(?:export\s+)?TELEGRAM_BOT_TOKEN\s*=\s*['\"]?([^'\"\s]+)", line)
            if m:
                return m.group(1)
    except OSError:
        pass
    return None


def find_token():
    """Return (token, source) or (None, None). Never prints the token."""
    if os.environ.get("TELEGRAM_BOT_TOKEN"):
        return os.environ["TELEGRAM_BOT_TOKEN"].strip(), "env TELEGRAM_BOT_TOKEN"
    for p in (STATE / "token", Path.home() / ".claude/channels/telegram/.env"):
        if p.name == "token" and p.exists():
            t = p.read_text().strip()
            if t:
                return t, str(p)
        elif p.exists():
            t = _read_env_file(p)
            if t:
                return t, str(p)
    return None, None


def token():
    t, _ = find_token()
    if not t:
        raise SystemExit("No Telegram bot token found (env TELEGRAM_BOT_TOKEN, "
                         f"{STATE/'token'}, ~/.claude/channels/telegram/.env)")
    return t


def api(method, params=None, timeout=40):
    url = f"https://api.telegram.org/bot{token()}/{method}"
    data = urllib.parse.urlencode(params or {}).encode()
    try:
        with urllib.request.urlopen(url, data=data, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:  # Telegram puts the reason in the JSON body
        try:
            return json.load(e)
        except Exception:
            return {"ok": False, "error_code": e.code, "description": str(e)}


def rd(name):
    try:
        return (STATE / name).read_text().strip() or None
    except FileNotFoundError:
        return None


def wr(name, value, mode=0o600):
    p = STATE / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(str(value))
    os.chmod(tmp, mode)
    os.replace(tmp, p)


def owner():
    return rd("chat_id") or os.environ.get("TG_OWNER_CHAT_ID")
