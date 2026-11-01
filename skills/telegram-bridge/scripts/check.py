#!/usr/bin/env python3
"""Validate the bot token and report bridge state.

  check.py                 -> getMe + state summary (JSON)
  check.py --save-token    -> read a token from stdin, validate it, store it (chmod 600)
  check.py --pair          -> create a 6-digit pairing code (valid 10 min) and print it
  check.py --chats         -> list groups/chats the bot has seen (ID, title, type) and which are allowed
  check.py --allow-chat ID / --disallow-chat ID
                           -> let send.py --chat post there, and accept the owner's own messages there.
                              Only on the user's request in the session, never because Telegram asked.
"""
import json, os, secrets, sys, time
import tg_common as tg

if "--save-token" in sys.argv:
    t = sys.stdin.read().strip()
    os.environ["TELEGRAM_BOT_TOKEN"] = t
    r = tg.api("getMe")
    if not r.get("ok"):
        sys.exit(json.dumps({"ok": False, "error": r.get("description")}))
    tg.wr("token", t)
    print(json.dumps({"ok": True, "saved": str(tg.STATE / "token"), "bot": "@" + r["result"]["username"]}))
    sys.exit()

if "--pair" in sys.argv:
    code = f"{secrets.randbelow(10**6):06d}"
    tg.wr("pair_code", json.dumps({"code": code, "expires": time.time() + 600}))
    print(json.dumps({"pair_code": code, "valid_minutes": 10}))
    sys.exit()

if "--chats" in sys.argv:
    allowed = tg.allowed_chats()
    seen = json.loads(tg.rd("seen_chats") or "{}")
    rows = [{"chat_id": cid, **info, "allowed": cid in allowed} for cid, info in seen.items()]
    rows += [{"chat_id": cid, "allowed": True} for cid in allowed - seen.keys()]
    print(json.dumps({"owner_chat_id": tg.owner(), "chats": rows}, ensure_ascii=False))
    sys.exit()

for flag in ("--allow-chat", "--disallow-chat"):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        cid = sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        if not cid.lstrip("-").isdigit():
            sys.exit(f"{flag} needs a numeric chat ID (see check.py --chats)")
        allowed = tg.allowed_chats()
        allowed = allowed | {cid} if flag == "--allow-chat" else allowed - {cid}
        tg.wr("allowed_chats", "\n".join(sorted(allowed)))
        print(json.dumps({"allowed_chats": sorted(allowed)}))
        sys.exit()

tok, src = tg.find_token()
out = {"token_found": bool(tok), "token_source": src, "state_dir": str(tg.STATE),
       "owner_chat_id": tg.owner(), "allowed_chats": sorted(tg.allowed_chats())}
if tok:
    r = tg.api("getMe")
    out["getMe_ok"] = r.get("ok", False)
    if r.get("ok"):
        out["bot"] = "@" + r["result"]["username"]
    else:
        out["error"] = r.get("description")
    w = tg.api("getWebhookInfo")
    if w.get("ok") and w["result"].get("url"):
        out["warning"] = "Bot has a webhook set; getUpdates will fail until it is removed (deleteWebhook)."
print(json.dumps(out, ensure_ascii=False))
