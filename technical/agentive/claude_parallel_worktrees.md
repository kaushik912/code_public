# Walkthrough: Building "todo persistence" 3 ways in parallel

A worked example of git worktrees + parallel agents. We took a tiny in-memory
todo CLI and had **three agents implement persistence at the same time** — one
using JSON, one CSV, one SQLite — then compared the three and merged the best.

Everything lives under `~/GitHub/tac_code/worktrees/`.

```
worktrees/
  todo/          <- main branch (base app + PLAN.md + final merged code)
  todo-json/     <- agent-json branch    (during the run)
  todo-csv/      <- agent-csv branch      (during the run)
  todo-sqlite/   <- agent-sqlite branch   (during the run)
```

---

## The base app (the starting point)

`todo/todo.py` — an in-memory todo CLI:

```python
#!/usr/bin/env python3
"""Tiny todo CLI (in-memory — todos vanish when the process exits)."""
import sys

TODOS = []

def add(text):
    TODOS.append(text)
    print(f"added: {text}")

def list_all():
    for i, t in enumerate(TODOS):
        print(f"{i}: {t}")

def main(argv):
    if not argv:
        print("commands: add <text> | list")
        return
    cmd, rest = argv[0], argv[1:]
    if cmd == "add":
        add(" ".join(rest))
    elif cmd == "list":
        list_all()
    else:
        print(f"unknown command: {cmd}")

if __name__ == "__main__":
    main(sys.argv[1:])
```

The flaw we set out to fix:

```bash
python3 todo.py add "buy milk"
python3 todo.py list      # prints NOTHING
```

Nothing prints because each command is a fresh process and `TODOS = []` lives
only in memory. **That missing persistence is the feature we parallelized.**

---

## The shared plan (`todo/PLAN.md`)

One spec, committed so every worktree inherits it. It deliberately leaves the
**storage format up to the agent** — that under-specification is what makes the
three attempts diverge and the comparison worthwhile. Full contents of
`todo/PLAN.md`:

```markdown
# Feature: make todos persist across runs

Right now todos live in memory and vanish when the process exits.

## Requirements
1. `add <text>` must save so a later `todo.py list` (new process) still shows it.
2. `list` reads from the saved store.
3. Add a `done <index>` command that removes/marks a todo as complete.
4. Single-file CLI, standard library only, store the data file next to the script.

## Acceptance check
    python3 todo.py add "buy milk"
    python3 todo.py add "call mom"
    python3 todo.py list        # new process -> shows both

You choose the storage format. Optimize for correctness and simplicity.
```

---

## Step-by-step (exactly what we ran)

### 1. Base + plan committed on `main`
```bash
cd ~/GitHub/tac_code/worktrees/todo
git add -A && git commit -m "base: in-memory todo CLI"
git add PLAN.md && git commit -m "add shared feature plan"
```

### 2. Three worktrees, one per storage idea
```bash
git worktree add -b agent-json   ../todo-json   main
git worktree add -b agent-csv    ../todo-csv    main
git worktree add -b agent-sqlite ../todo-sqlite main
git worktree list      # 4 folders, 4 branches, all at the plan commit
```
Each worktree is a real separate folder with its own `todo.py`, sharing one
`.git`. That's why three agents can edit "todo.py" at once without conflicts.

### 3. Launch three headless agents in parallel
Same plan to each; the only difference is a storage hint to force divergence.
```bash
cd ~/GitHub/tac_code/worktrees/todo-json && claude -p 'Read PLAN.md and implement every requirement by editing todo.py in this directory. If storage format is my choice and you are unsure, use a JSON file. Run the acceptance check from PLAN.md, fix failures, then: git add -A && git commit -m "feat: persist todos (json)". Report your storage choice and the acceptance output.' --allowedTools 'Read,Edit,Write,Bash' > /tmp/agent-json.log 2>&1 &

cd ~/GitHub/tac_code/worktrees/todo-csv && claude -p 'Read PLAN.md and implement every requirement by editing todo.py in this directory. If storage format is my choice and you are unsure, use a CSV file. Run the acceptance check from PLAN.md, fix failures, then: git add -A && git commit -m "feat: persist todos (csv)". Report your storage choice and the acceptance output.' --allowedTools 'Read,Edit,Write,Bash' > /tmp/agent-csv.log 2>&1 &

cd ~/GitHub/tac_code/worktrees/todo-sqlite && claude -p 'Read PLAN.md and implement every requirement by editing todo.py in this directory. If storage format is my choice and you are unsure, use sqlite3 from the stdlib. Run the acceptance check from PLAN.md, fix failures, then: git add -A && git commit -m "feat: persist todos (sqlite)". Report your storage choice and the acceptance output.' --allowedTools 'Read,Edit,Write,Bash' > /tmp/agent-sqlite.log 2>&1 &

cd ~/GitHub/tac_code/worktrees/todo && jobs      # wait for all three "Done"
```

### 4. Verify from git (NOT from what the agents say)
```bash
for b in json csv sqlite; do
  echo "=== agent-$b ==="; git -C ~/GitHub/tac_code/worktrees/todo-$b log --oneline -1
done
```
Want three real `feat: persist todos (...)` commits. If a branch is still at the
plan commit, that agent didn't finish — `cat /tmp/agent-<name>.log` to see why.

### 5. Compare the three
```bash
for b in json csv sqlite; do
  echo "=== agent-$b ==="
  git -C ~/GitHub/tac_code/worktrees/todo-$b diff --stat main -- todo.py
  echo "committed a runtime data file? ->" $(git -C ~/GitHub/tac_code/worktrees/todo-$b ls-files | grep -E 'todos?\.(json|csv|db)' || echo "no (clean)")
done
```
How the three compared:
| branch | store | notes |
|---|---|---|
| agent-json   | `todos.json` | smallest diff, human-readable — simplest thing that works |
| agent-csv    | `todos.csv`  | readable too, clunkier for quoted/nested text |
| agent-sqlite | `todos.db`   | most robust, but binary store + most code; overkill here |

Read any candidate without switching branches (it's just a folder):
```bash
git -C ~/GitHub/tac_code/worktrees/todo diff main..agent-json -- todo.py
```

### 6. Merge the winner
For a tiny todo CLI, **json** won (simplest full solution). Merge just that branch:
```bash
cd ~/GitHub/tac_code/worktrees/todo
git merge --no-ff agent-json -m "merge: persist todos (winner: agent-json)"
python3 todo.py add "buy milk"
python3 todo.py list      # now SHOWS the todo in a fresh process — flaw fixed
```

### 7. Teardown (the other two were free experiments)
```bash
cd ~/GitHub/tac_code/worktrees/todo
git worktree remove ../todo-json
git worktree remove ../todo-csv
git worktree remove ../todo-sqlite
git branch -D agent-json agent-csv agent-sqlite
git worktree list         # back to just main; winning code already merged
```

---

## Two gotchas we actually hit

1. **`--dangerously-skip-permissions` was blocked** (enterprise policy on this
   machine). Headless `claude -p` then couldn't write and silently did nothing.
   Fix: pre-authorize exactly the tools with `--allowedTools 'Read,Edit,Write,Bash'`.

2. **Agents' self-reports lied.** On the first run `jobs` showed "Done" but every
   branch was still at the plan commit — no work committed. Checking `git log`
   caught it. **Always verify from git state, never from the agent saying "done."**

---

## Recommended: `claude -w <name>` in the CLI (verified working, minimal config)

**What actually works best — verified.** The CLI's `-w` / `--worktree` flag
creates an isolated, named worktree and drops you into a session inside it, with
**no extra config**. Give each approach a descriptive name:

```bash
cd ~/GitHub/tac_code/worktrees/todo   # the repo with the base todo.py

claude -w json-approach     # session #1, isolated worktree for the JSON attempt
claude -w csv-approach      # session #2, isolated worktree for the CSV attempt
claude -w sqlite-approach   # session #3, isolated worktree for the SQLite attempt
```

Verified behavior:
- Worktree path: **`<repo>/.claude/worktrees/<name>`** (nested + managed, not a
  sibling `../`). The `<name>` you pass is exactly this folder name.
- Branch name: **`worktree-<name>`** (auto-prefixed), created from current HEAD.
- The worktree is **locked** while the session owns it → manual removal needs
  `git worktree remove -f -f <path>`.
- Add `--tmux` to split the worktree session into iTerm2/tmux panes.

### Run the prompt yourself (interactive — no `-p`)
Prefer **not** using `-p` for real work: persistence (or any non-trivial feature)
usually takes a few back-and-forth iterations, and `-p` is one-shot/headless. So
just start the named-worktree session and type the prompt in the chat, iterating
until the implementation is right:

```bash
claude -w json-approach
# then, in the interactive session, type:
#   "Read todo.py and add persistence using a JSON file so todos survive
#    restarts. Add a `done <index>` command. Then run it to prove it works."
# iterate in chat until it's correct, then ask it to commit.
```
Repeat in two more terminals/tabs with `csv-approach` and `sqlite-approach`.
Because each is its own worktree, the three `todo.py` files never collide.

Then compare and merge from the main repo (branches are `worktree-json-approach`,
`worktree-csv-approach`, `worktree-sqlite-approach`):
```bash
git -C ~/GitHub/tac_code/worktrees/todo diff --stat main..worktree-json-approach -- todo.py
git merge --no-ff worktree-json-approach -m "merge: persist todos (winner)"
```

### Manual vs `-w` — both are CLI, both verified
| | Manual `git worktree add ../todo-json` | `claude -w json-approach` |
|---|---|---|
| Worktree location | sibling `../todo-json` (you pick) | `.claude/worktrees/json-approach` |
| Branch name | you choose (`agent-json`) | auto `worktree-json-approach` |
| Setup effort | 3 `git worktree add` lines | none — the flag does it |
| Inspecting side by side | easy, obvious sibling folders | folders tucked under `.claude/` |
| Cleanup | `git worktree remove` (unlocked) | `git worktree remove -f -f` (locked) |
| Best when | you want to eyeball/cherry-pick across attempts | you want named worktrees + an interactive session per attempt |

For our 3-storage bake-off both CLI paths isolate correctly. Use **manual** when
you want the three `todo.py` files in plain sibling folders to diff; use
**`claude -w <name>`** when you want each approach in its own named, ready-to-chat
session.

## Why this specific setup was a good demo
- The feature ("persist todos") had **genuine design freedom**, so JSON/CSV/SQLite
  were all valid — the parallel run turned into a real design comparison.
- Comparing three finished, tested implementations at once = free code review;
  divergence surfaces trade-offs (readable-text vs binary, small diff vs robust)
  you'd never see from iterating a single approach.
- The losing branches cost nothing to create and nothing to delete.
