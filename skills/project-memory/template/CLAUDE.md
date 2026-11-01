# <Project> memory

Durable memory for <Project>. A fresh agent reads this folder and continues the work without a prompt
from the user. Task state lives here, not in the conversation, so `/clear` is safe.

## Resume here

1. Read [`rules.md`](rules.md) and [`lessons.md`](lessons.md).
2. Open [`tasks/INDEX.md`](tasks/INDEX.md) and find the active task.
3. Read that task's `README.md`: `Status` first, then the end of `## Log`.
4. Check the real state of the environment before you trust a file: <command, for example `bin/status`>.
5. Continue from the task's `Status`. If an open question blocks you, ask the user.

## The project

<What the product does, in 3 to 5 lines.>

**Key terms:** <term> (<meaning>); <term> (<meaning>).

## Workspace map

Paths are relative to the workspace root `<path>`.

| Folder | What it is |
|---|---|
| `memory/` | This folder. Its own private repo `<org>/<project>-memory`. |
| `<repo>/` | <purpose> |

**Where common things live:** <feature> → `<path>`.

## Files

| File | Content |
|---|---|
| [`rules.md`](rules.md) | Everything the user decided: how we work, and product or technical decisions. |
| [`lessons.md`](lessons.md) | One-line principles from real incidents. |
| [`tasks/`](tasks/INDEX.md) | One folder per task. `INDEX.md` lists them. |
| [`docs/`](docs/README.md) | One subfolder per topic: runbook, facts and scripts together. |
| [`secrets/`](secrets/README.md) | Credentials, encrypted with git-crypt. Refer to a file by path. Never print its content. |

## How to work a task

- **Start:** copy `tasks/_TEMPLATE.md` to `tasks/<YYYY-MM-DD>-<slug>/README.md` and add a line to `tasks/INDEX.md`.
- **During:** keep `Status` current, and add one `## Log` line per event. Run `date` for the time.
- **Result:** write a line that starts with `RESULT:` for each outcome the team must know, with numbers and PR refs.
- **Ruling:** if the user decides something, add it to `rules.md`, dated and tagged with the task slug.
- **Done:** write `Outcome`, move durable facts to `docs/`, `rules.md` or `lessons.md`, and move the task to Done in `INDEX.md`.
- **Before you stop or clear:** update `Status` and `## Log`. The next agent knows only what these files say.
