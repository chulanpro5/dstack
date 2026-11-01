#!/usr/bin/env python3
"""Long-poll getUpdates and print one JSON line per message from the owner chat.

Two ways to run it:
  poll.py                          loop forever (Monitor tool: every stdout line is an event)
  poll.py --once [--max-seconds N] exit after the first batch that has an event, or after N seconds
                                   with no output (Bash run_in_background: one wake-up per message)
Events:
  {"chat_id","from","text"[,"file"]}   a message from the owner
  {"event":"owner_registered",...}       pairing succeeded
  (button presses on permission requests are handled silently, see permission_hook.py)
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
ONCE = "--once" in sys.argv
DEADLINE = time.time() + (float(sys.argv[sys.argv.index("--max-seconds") + 1])
                          if "--max-seconds" in sys.argv else float("inf"))
emitted = False


def emit(obj):
    global emitted
    emitted = True
    print(json.dumps(obj, ensure_ascii=False), flush=True)


fails = 0
while True:
    if ONCE and emitted:
        sys.exit(0)
    if time.time() > DEADLINE:
        sys.exit(0)
    params = {"timeout": 25, "allowed_updates": json.dumps(["message", "callback_query"])}
    if tg.rd("offset"):
        params["offset"] = tg.rd("offset")
    try:
        data = tg.api("getUpdates", params)
    except Exception as e:  # network errors
        data = {"ok": False, "description": str(e)}
    if not data.get("ok"):
        if data.get("error_code") == 409:
            emit({"event": "taken_over", "detail": data.get("description")})
            sys.exit(0)
        fails += 1
        if fails == 3:
            emit({"event": "error", "detail": str(data.get("description"))[:200]})
        time.sleep(10)
        continue
    fails = 0
    for u in data["result"]:
        tg.wr("offset", u["update_id"] + 1)
        cq = u.get("callback_query")
        if cq:  # button press on a permission request (see permission_hook.py)
            data = cq.get("data", "")
            ok = tg.owner() and str(cq["from"]["id"]) == tg.owner() and data.startswith("perm:")
            if ok:
                _, rid, choice = data.split(":", 2)
                (tg.STATE / "decisions").mkdir(exist_ok=True)
                tg.wr(f"decisions/{rid}", choice)
            tg.api("answerCallbackQuery", {"callback_query_id": cq["id"],
                                           "text": ("Đã ghi nhận" if ok else "Không có quyền")})
            continue
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
                emit({"event": "owner_registered", "chat_id": cid,
                      "from": m.get("from", {}).get("first_name")})
            continue  # unpaired: ignore everything else silently
        if cid != own:
            continue
        ev = {"chat_id": cid, "from": m.get("from", {}).get("first_name"),
              "text": text or "[non-text message]"}
        for kind in ("photo", "document", "voice", "audio", "video"):
            if kind in m:
                f = m[kind][-1] if kind == "photo" else m[kind]
                ev["file"] = {"kind": kind, "file_id": f["file_id"], "name": f.get("file_name")}
        emit(ev)
