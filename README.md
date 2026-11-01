# dstack

A personal collection of [Claude Code](https://claude.com/claude-code) skills.

## Skills

| Skill | What it does |
|---|---|
| [`project-memory`](skills/project-memory/SKILL.md) | Sets up and maintains a durable `memory/` folder (a private git repo) at a workspace root, so any agent with a fresh context can resume the work: project map, user rules, lessons, and per-task status and logs. |
| [`telegram-bridge`](skills/telegram-bridge/SKILL.md) | Lets you talk to a Claude Code session (cloud or local) through your own Telegram bot: finds or asks for the bot token, pairs your chat with a one-time code, waits for messages in a background poller, replies with text, images and files, restarts itself with an hourly scheduled task, and can optionally send permission prompts to Telegram as Allow/Deny buttons. |

## Install

dstack is a Claude Code plugin (and its own marketplace). Both skills come with it.

```
/plugin install dstack --marketplace chulanpro5/dstack
```

Skills are then available as `/dstack:project-memory` and `/dstack:telegram-bridge`.

### Claude Code on the web (cloud sessions)

Cloud sessions don't read your `~/.claude/settings.json`, so enable the plugin from each repository you work
in. Commit this `.claude/settings.json` to that repo:

```json
{
  "extraKnownMarketplaces": {
    "dstack": { "source": { "source": "github", "repo": "chulanpro5/dstack" } }
  },
  "enabledPlugins": { "dstack@dstack": true }
}
```

These two keys are read even when a session has several repositories. An organization admin can enable the
plugin for every session through managed settings instead.

For `telegram-bridge`, also set `TELEGRAM_BOT_TOKEN` in the cloud environment's environment variables so
every session finds the token without asking. To approve permission prompts from Telegram, set
`TG_PERMISSION_HOOK=1` there as well (see the skill).

### Without the plugin system

Copy a skill folder into `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/` (all projects) or
`<project>/.claude/skills/` (one project). The Telegram permission hook then needs to be added to your
settings by hand: copy the `PermissionRequest` entry from `hooks/hooks.json` and replace
`${CLAUDE_PLUGIN_ROOT}` with the path of this repo.

## Requirements

- `git`
- [`git-crypt`](https://github.com/AGWA/git-crypt), only if you want encrypted secrets in `memory/secrets/`
- `python3` (standard library only) for `telegram-bridge`
