#!/usr/bin/env python3
"""Claude Code PermissionRequest hook: ask the Telegram owner to allow or deny.

Reads the hook JSON from stdin, sends the owner a message with Allow / Deny buttons, and waits
for poll.py (which must be running) to record the button press in $TG_BRIDGE_DIR/decisions/.
On timeout or any error it prints nothing, so Claude Code falls back to its normal prompt.

settings.json:
  {"hooks": {"PermissionRequest": [{"matcher": "", "hooks": [
     {"type": "command", "command": "python3 <S>/permission_hook.py", "timeout": 600}]}]}}
"""
import json, os, secrets, sys, time
import tg_common as tg

WAIT = float(os.environ.get("TG_PERMISSION_WAIT", "540"))  # keep below the hook timeout


def summarize(ev):
    ti = ev.get("tool_input") or {}
    detail = ti.get("command") or ti.get("url") or ti.get("file_path") or json.dumps(ti, ensure_ascii=False)
    return f"🔐 Claude xin quyền: {ev.get('tool_name', '?')}\n\n{str(detail)[:1500]}"


def main():
    ev = json.load(sys.stdin)
    owner = tg.owner()
    if not owner:
        return
    rid = secrets.token_hex(6)
    kb = {"inline_keyboard": [[{"text": "✅ Cho phép", "callback_data": f"perm:{rid}:allow"},
                               {"text": "❌ Từ chối", "callback_data": f"perm:{rid}:deny"}]]}
    r = tg.api("sendMessage", {"chat_id": owner, "text": summarize(ev), "reply_markup": json.dumps(kb)})
    if not r.get("ok"):
        return
    mid = r["result"]["message_id"]
    path = tg.STATE / "decisions" / rid
    end = time.time() + WAIT
    while time.time() < end:
        if path.exists():
            choice = path.read_text().strip()
            path.unlink(missing_ok=True)
            tg.api("editMessageReplyMarkup", {"chat_id": owner, "message_id": mid})
            tg.api("sendMessage", {"chat_id": owner, "reply_to_message_id": mid,
                                   "text": "✅ Đã cho phép" if choice == "allow" else "❌ Đã từ chối"})
            decision = {"behavior": "allow"} if choice == "allow" else \
                       {"behavior": "deny", "message": "The user denied this via Telegram."}
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                                     "decision": decision}}))
            return
        time.sleep(1)
    tg.api("editMessageReplyMarkup", {"chat_id": owner, "message_id": mid})
    tg.api("sendMessage", {"chat_id": owner, "reply_to_message_id": mid,
                           "text": "⌛ Hết thời gian chờ, chuyển về hỏi trong app."})


try:
    main()
except Exception:
    pass  # never break Claude Code; fall back to the normal prompt
