#!/usr/bin/env python3
"""Validate the bot token and report bridge state.

  check.py                 -> getMe + state summary (JSON)
  check.py --save-token    -> read a token from stdin, validate it, store it (chmod 600)
  check.py --pair          -> create a 6-digit pairing code (valid 10 min) and print it
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

tok, src = tg.find_token()
out = {"token_found": bool(tok), "token_source": src, "state_dir": str(tg.STATE),
       "owner_chat_id": tg.owner()}
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
