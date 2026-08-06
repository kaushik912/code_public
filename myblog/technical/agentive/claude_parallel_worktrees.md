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

`todo/todo.py` — an in-memory todo CLI. The flaw we set out to fix:

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
three attempts diverge and the comparison worthwhile.

Key requirements: `add` must survive into a new process, `list` reads the store,
add a `done <index>` command, single-file + stdlib only, data file next to script.

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

## Why this specific setup was a good demo
- The feature ("persist todos") had **genuine design freedom**, so JSON/CSV/SQLite
  were all valid — the parallel run turned into a real design comparison.
- Comparing three finished, tested implementations at once = free code review;
  divergence surfaces trade-offs (readable-text vs binary, small diff vs robust)
  you'd never see from iterating a single approach.
- The losing branches cost nothing to create and nothing to delete.
