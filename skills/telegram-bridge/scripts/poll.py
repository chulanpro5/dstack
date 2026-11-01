#!/usr/bin/env python3
"""Long-poll getUpdates and print one JSON line per message from the owner chat.

Meant to run under the Monitor tool: every stdout line becomes an event.
Events:
  {"chat_id","from","text"[,"file"]}   a message from the owner
  {"event":"owner_registered",...}       pairing succeeded
  {"event":"taken_over"}                 another session started polling this bot; we exit
  {"event":"error",...}                  3 consecutive failures (transient ones stay quiet)
"""
import fcntl, json, sys, time
import tg_common as tg

lock = open(tg.STATE / "poll.lock", "w")
try:
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
except OSError:
    sys.exit(0)  # a poller is already running in this container

tg.token()  # fail fast if there is no token
fails = 0
while True:
    params = {"timeout": 25, "allowed_updates": json.dumps(["message"])}
    if tg.rd("offset"):
        params["offset"] = tg.rd("offset")
    try:
        data = tg.api("getUpdates", params)
    except Exception as e:  # network errors
        data = {"ok": False, "description": str(e)}
    if not data.get("ok"):
        if data.get("error_code") == 409:
            print(json.dumps({"event": "taken_over", "detail": data.get("description")}), flush=True)
            sys.exit(0)
        fails += 1
        if fails == 3:
            print(json.dumps({"event": "error", "detail": str(data.get("description"))[:200]}), flush=True)
        time.sleep(10)
        continue
    fails = 0
    for u in data["result"]:
        tg.wr("offset", u["update_id"] + 1)
        m = u.get("message")
        if not m:
            continue
        cid = str(m["chat"]["id"])
        text = m.get("text") or m.get("caption") or ""
        own = tg.owner()
        if own is None:
            pc = json.loads(tg.rd("pair_code") or "{}")
            if pc and time.time() < pc["expires"] and text.strip() == pc["code"]:
                tg.wr("chat_id", cid)
                (tg.STATE / "pair_code").unlink(missing_ok=True)
                print(json.dumps({"event": "owner_registered", "chat_id": cid,
                                  "from": m.get("from", {}).get("first_name")}), flush=True)
            continue  # unpaired: ignore everything else silently
        if cid != own:
            continue
        ev = {"chat_id": cid, "from": m.get("from", {}).get("first_name"),
              "text": text or "[non-text message]"}
        for kind in ("photo", "document", "voice", "audio", "video"):
            if kind in m:
                f = m[kind][-1] if kind == "photo" else m[kind]
                ev["file"] = {"kind": kind, "file_id": f["file_id"], "name": f.get("file_name")}
        print(json.dumps(ev, ensure_ascii=False), flush=True)
