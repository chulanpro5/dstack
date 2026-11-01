# dstack

A personal collection of [Claude Code](https://claude.com/claude-code) skills.

## Skills

| Skill | What it does |
|---|---|
| [`project-memory`](skills/project-memory/SKILL.md) | Sets up and maintains a durable `memory/` folder (a private git repo) at a workspace root, so any agent with a fresh context can resume the work: project map, user rules, lessons, and per-task status and logs. |

## Install

Copy a skill folder into your Claude Code skills directory:

```sh
git clone https://github.com/chulanpro5/dstack.git
cp -R dstack/skills/project-memory "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/"
```

To use it in a single project only, copy it to `<project>/.claude/skills/` instead.

Then ask Claude to "set up project memory for this workspace", or invoke `/project-memory`.

## Requirements

- `git`
- [`git-crypt`](https://github.com/AGWA/git-crypt), only if you want encrypted secrets in `memory/secrets/`
