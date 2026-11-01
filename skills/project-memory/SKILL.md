---
name: project-memory
description: Set up and keep a durable `memory/` folder for a project, so any agent with a fresh context can read it and continue the work without a prompt from the user. Use when the user asks to set up, init or scaffold project memory (or a handbook) for a workspace; to start, resume, update or close a task in `memory/tasks/`; to record a rule, decision or lesson; or before `/clear` or the end of a session in a workspace that has a `memory/` folder.
---

# Project memory

`memory/` is a private git repo at the workspace root. It holds the project's durable state: what the
project is, what the user decided, what we learned, and where each task stands. The conversation is
temporary. The files are the truth.

```
memory/
├── CLAUDE.md      # Entry: what the project is, workspace map, "resume here" steps, file index
├── rules.md       # Everything the user decided: "How we work" + "Decisions", one dated line each
├── lessons.md     # One-line principles from real incidents
├── tasks/
│   ├── INDEX.md           # Active on top, Done below
│   ├── _TEMPLATE.md
│   └── YYYY-MM-DD-slug/
│       ├── README.md      # Goal, Scope, Status, PRs, Outcome, then ## Log
│       └── evidence/      # Git-ignored
├── docs/          # One subfolder per topic: runbook, facts and scripts together
└── secrets/       # git-crypt; README.md lists each file
```

The template for every file is in `template/` next to this file.

## Set up memory for a project

1. Find the workspace root. Ask the user if it is not clear. If `memory/` already exists, stop and ask.
2. Copy the template: `cp -R <this skill's folder>/template/. <root>/memory/`.
3. Fill `memory/CLAUDE.md` from what you can see: list the root, read each repo's README, and write the
   project summary and the workspace map. Mark facts you cannot confirm with `<TODO>`. Do not invent them.
4. Ask the user for the first rules ("How we work"): what you may do alone, what needs them, the PR
   flow, and the checks to run. Write each answer as a dated line in `rules.md`.
5. Run `git init` in `memory/`. If the user wants secrets in the repo, run `git-crypt init`, tell the
   user to export the key to a password manager, and run `git-crypt status -e` before the first commit.
   If not, delete `secrets/` and the git-crypt lines in `.gitattributes`.
6. Make the memory load at session start: add the line `@memory/CLAUDE.md` to the workspace root
   `CLAUDE.md` (create it if it does not exist). If other agents work there, add an `AGENTS.md` that
   points to `memory/CLAUDE.md`.
7. Commit. Ask before you create a remote repo or push.

## Resume

1. Read `memory/CLAUDE.md`, `rules.md` and `lessons.md`.
2. Open `tasks/INDEX.md`. If more than one task is active and the user did not name one, ask which.
3. Read the task's `Status`, `Open questions` and the end of `## Log`.
4. Check the real state (git branches, running services, PR states) before you trust the files. If they
   disagree, the real state wins: fix the file.

## Keep it current

- **Start a task:** copy `tasks/_TEMPLATE.md` to `tasks/<YYYY-MM-DD>-<slug>/README.md`, fill Goal and
  Scope, and add a line under Active in `INDEX.md`.
- **Log:** one line per event, newest last, `YYYY-MM-DD HH:MM <what / why>`. Run `date` for the time.
  Never estimate it. No narration of effort.
- **Result:** if an outcome is reportable (a decision, a measured finding, something merged or live, a
  deliverable), start the log text with `RESULT:` and give its numbers and PR refs. One line per result.
- **Rule:** if the user decides something, add it to `rules.md` with the next ID, the date and the
  task slug. If it replaces a rule, edit or delete the old line. A proposal from an agent is not a rule.
  If a rule changes the task's scope, update Goal, Scope and Status in the same edit.
- **Lesson:** if an incident teaches a general principle, add one line to `lessons.md`. Put the fix steps
  in `docs/<topic>/`.
- **Fact:** if you learn how a system works, edit the right `docs/<topic>/` file in place.
- **Done:** fill `Outcome`, move durable facts out of the task, set Status to done, and move the
  `INDEX.md` line to Done with its outcome.
- **Before `/clear`, compaction or the end of a session:** update `Status` and `## Log`, then commit.

## Rules for the content

- Write for an agent with no context: full paths, real commands, current numbers. Give a rule's meaning
  next to its ID, never the ID alone.
- One fact in one place. Link to it; do not copy it.
- If a fact changes, edit it in place. Do not append a contradiction.
- Keep `CLAUDE.md` short. It loads in every session. Move detail to `docs/`.
- Binaries go in the task's `evidence/` and stay out of git. Cite them by filename.
- Never print the content of a file in `secrets/`. Refer to it by path.
- Subagents report to the main session. Only the main session edits `memory/`, unless the user says otherwise.
