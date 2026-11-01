# dstack

A personal collection of [Claude Code](https://claude.com/claude-code) skills.

## Skills

| Skill | What it does |
|---|---|
| [`project-memory`](skills/project-memory/SKILL.md) | Sets up and maintains a durable `memory/` folder (a private git repo) at a workspace root, so any agent with a fresh context can resume the work: project map, user rules, lessons, and per-task status and logs. |
| [`telegram-bridge`](skills/telegram-bridge/SKILL.md) | Lets you talk to a Claude Code session (cloud or local) through your own Telegram bot: finds or asks for the bot token, pairs your chat with a one-time code, listens with the Monitor tool, replies with text, images and files, and restarts itself with an hourly scheduled task. |

## Install

Copy a skill folder into your Claude Code skills directory:

```sh
git clone https://github.com/chulanpro5/dstack.git
cp -R dstack/skills/project-memory "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/"
```

To use it in a single project only, copy it to `<project>/.claude/skills/` instead.

Then ask Claude to "set up project memory for this workspace", or invoke `/project-memory`.

### Claude Code on the web (cloud sessions)

Cloud sessions load skills from the repository they run on. Copy the skill into that repo's `.claude/skills/`
and commit it, then run `/telegram-bridge` in any session on that repo. Set `TELEGRAM_BOT_TOKEN` in the cloud
environment's environment variables so every session finds the token without asking.

## Requirements

- `git`
- [`git-crypt`](https://github.com/AGWA/git-crypt), only if you want encrypted secrets in `memory/secrets/`
- `python3` (standard library only) for `telegram-bridge`
