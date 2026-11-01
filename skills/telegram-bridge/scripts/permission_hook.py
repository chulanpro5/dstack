#!/usr/bin/env python3
"""Claude Code PermissionRequest hook: ask the Telegram owner to allow or deny.

Reads the hook JSON from stdin, sends the owner a message with Allow / Deny buttons, and waits
for poll.py (which must be running) to record the button press in $TG_BRIDGE_DIR/decisions/.
On timeout or any error it prints nothing, so Claude Code falls back to its normal prompt.
Opt-in: does nothing unless TG_PERMISSION_HOOK=1, an owner chat is paired and poll.py is running.

settings.json:
  {"hooks": {"PermissionRequest": [{"matcher": "", "hooks": [
     {"type": "command", "command": "python3 <S>/permission_hook.py", "timeout": 600}]}]}}
"""
import fcntl, json, os, secrets, sys, time
import tg_common as tg

WAIT = float(os.environ.get("TG_PERMISSION_WAIT", "540"))  # keep below the hook timeout


def summarize(ev):
    ti = ev.get("tool_input") or {}
    detail = ti.get("command") or ti.get("url") or ti.get("file_path") or json.dumps(ti, ensure_ascii=False)
    return f"🔐 Claude xin quyền: {ev.get('tool_name', '?')}\n\n{str(detail)[:1500]}"


def poller_running():
    """poll.py holds an exclusive flock on poll.lock while it runs."""
    try:
        with open(tg.STATE / "poll.lock", "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(f, fcntl.LOCK_UN)
            return False
    except OSError:
        return True


def main():
    if os.environ.get("TG_PERMISSION_HOOK") != "1":
        return  # opt-in only
    ev = json.load(sys.stdin)
    owner = tg.owner()
    if not owner or not tg.find_token()[0] or not poller_running():
        return  # nobody could record a button press; use the normal prompt
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
