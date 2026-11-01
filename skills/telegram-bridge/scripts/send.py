#!/usr/bin/env python3
"""Send to the owner chat (or, with --chat, to a chat allowed by check.py --allow-chat).

  send.py "text"                      plain text (auto-split at 4096 chars)
  send.py -- "--text"                 text that starts with "--"
  send.py --file PATH [--caption C]   image -> sendPhoto, anything else -> sendDocument
  send.py --get FILE_ID [--out DIR]   download a file the owner sent (prints local path)
  --chat ID                           send text/--file to that chat instead of the owner chat
  --help                              print this help (nothing is sent)
"""
import json, mimetypes, sys, uuid, urllib.request
from pathlib import Path
import tg_common as tg

def multipart(method, fields, file_field, path):
    b = uuid.uuid4().hex
    body = b""
    for k, v in fields.items():
        body += f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
    body += (f'--{b}\r\nContent-Disposition: form-data; name="{file_field}"; filename="{Path(path).name}"\r\n'
             f"Content-Type: {ctype}\r\n\r\n").encode() + Path(path).read_bytes() + f"\r\n--{b}--\r\n".encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{tg.token()}/{method}", data=body,
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)

args = sys.argv[1:]
if "--" in args:  # everything after "--" is message text, even if it looks like a flag
    i = args.index("--")
    args, literal = args[:i], args[i + 1:]
else:
    literal = []
if args[:1] in (["--help"], ["-h"]):
    print(__doc__.strip())
    sys.exit()

chat = tg.owner()
if not chat:
    sys.exit("No owner chat yet: pair first (check.py --pair).")
if "--chat" in args:
    i = args.index("--chat")
    if i + 1 >= len(args):
        sys.exit("--chat needs a chat ID")
    target = args[i + 1]
    del args[i:i + 2]
    if target != chat and target not in tg.allowed_chats():
        sys.exit(f"Chat {target} is not allowed. The user can allow it in the session: "
                 "check.py --allow-chat ID (see check.py --chats).")
    chat = target

KNOWN = {"--get": 1, "--out": 1, "--file": 1, "--caption": 1}
i = 0
while i < len(args):  # refuse unknown flags instead of sending them as text
    if args[i].startswith("--"):
        if args[i] not in KNOWN:
            sys.exit(f"Unknown option {args[i]} (see send.py --help; use -- before text starting with --)")
        i += KNOWN[args[i]]
    i += 1

if args[:1] == ["--get"]:
    f = tg.api("getFile", {"file_id": args[1]})["result"]
    out = Path(args[args.index("--out") + 1] if "--out" in args else tg.STATE / "downloads")
    out.mkdir(parents=True, exist_ok=True)
    dest = out / Path(f["file_path"]).name
    urllib.request.urlretrieve(f"https://api.telegram.org/file/bot{tg.token()}/{f['file_path']}", dest)
    print(dest)
elif args[:1] == ["--file"]:
    path = args[1]
    cap = args[args.index("--caption") + 1] if "--caption" in args else ""
    is_img = (mimetypes.guess_type(path)[0] or "").startswith("image/") and Path(path).stat().st_size < 10_000_000
    r = multipart("sendPhoto" if is_img else "sendDocument", {"chat_id": chat, "caption": cap[:1024]},
                  "photo" if is_img else "document", path)
    print("ok" if r.get("ok") else r)
else:
    text = " ".join(args + literal) if args or literal else sys.stdin.read()
    for i in range(0, max(len(text), 1), 4000):
        r = tg.api("sendMessage", {"chat_id": chat, "text": text[i:i + 4000]})
        if not r.get("ok"):
            sys.exit(str(r))
    print("ok")
