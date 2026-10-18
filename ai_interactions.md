# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

I used Claude Code (agent mode in VS Code) for the stretch challenges. I pasted in all five challenges at once and let the agent work through them, reading files, editing several of them, running the demo and tests, and fixing problems along the way.

**What task did you give the agent?**

Add four things to PawPal+:

1. A new algorithm beyond the basic requirements. We picked **"next available slot"**, which finds the earliest free time today where a new task fits.
2. Saving pets and tasks to `data.json` so they're still there next time.
3. A "priority first, then time" sort.
4. Nicer output: emojis, colors, and tables.

It also had to document all of it in the README.

**What did the agent do?**

| File | What changed |
|---|---|
| `pawpal_system.py` | Added `Scheduler.find_next_available_slot()`, `Scheduler.sort_by_priority_then_time()`, `to_dict()` / `from_dict()` on `Task`, `Pet`, and `Owner`, `Owner.save_to_json()` / `Owner.load_from_json()`, and emoji maps for categories and priorities. It also rewrote `Task.next_occurrence()` so weekly tasks stay on the same weekday (see the Prompt Comparison below). |
| `app.py` | Loads `data.json` at startup and saves after every change. Added a "Start over" button, a "Pick the next free time for me" checkbox, a "Sort by" dropdown, and emojis in the tables. |
| `main.py` | Rewrote the demo to print `tabulate` tables with emojis and colored status. Added sections for priority sorting, free slots, and save/load. |
| `tests/test_pawpal.py` | Added 10 tests (36 total): weekly weekday rules, priority-then-time sorting, free slots, and saving/loading. |
| `requirements.txt` | Added `tabulate[widechars]`. |
| `.gitignore` | Ignores `data.json`. |
| `diagrams/uml_final.mmd`, `README.md` | Updated the diagram and added sections for the new features, persistence, priority scheduling, and formatting. |

The steps it took:

1. Read the existing code.
2. Started two background agents for the model comparison.
3. Added the new methods and checked them with a quick script.
4. Installed `tabulate` into the virtual environment.
5. Updated the CLI demo and the app.
6. Tested the app headlessly with Streamlit's testing tool, including closing the session and opening a new one to check that the data loaded back.
7. Wrote the new tests and ran the full suite.
8. Updated the docs.

**What did you have to verify or fix manually?**

- **Broken demo code:** the agent wrote a weird leftover line in `main.py` (an `if False else` expression) and had to go back and clean it up.
- **A demo that showed nothing:** the first version showed identical tables for "sorted by time" and "sorted by priority", because of the example data. The two sorts weren't actually different in the demo, so it moved the thyroid meds to 20:00 to make the difference visible.
- **A real bug:** the model comparison showed that the old recurrence logic (`max(due_date, today) + 7 days`) moved weekly tasks to a different weekday when they were finished late. We fixed it and added tests for it.
- **Emoji alignment:** emojis broke the table columns until `tabulate[widechars]` was installed.
- **Earlier phases:** I made several calls myself:
  - I chose to add the start time and pet name to the design right away instead of waiting.
  - I asked for the reflection and README to be rewritten in simpler English.
  - I asked that commits use only my name, with no AI co-author line.

---

## Prompt Comparison (SF11)

**Task:** the logic for rescheduling recurring tasks, especially weekly ones. When a task is marked done, `next_occurrence()` should return the next copy. Weekly tasks should stay on the same weekday, a late task shouldn't come back in the past, and an early task shouldn't repeat on the day it was already due.

I gave the exact same prompt (with my `Task` dataclass) to two different models. Both were run as separate agents from Claude Code, without access to my files. I only have Claude models available in my tools, so I compared a bigger model with a smaller one.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Sonnet (via Claude Code agent) | Claude Haiku (via Claude Code agent) |
| **Prompt** | "Write `next_occurrence(self) -> Task \| None` … weekly tasks should stay on the same weekday … if completed late, the next one must not be in the past … if completed early, no duplicate on the date it was already due. Explain your approach, give the code, and list edge cases." | Same prompt, word for word |
| **Response summary** | Step forward from the original due date by whole weeks: `k = max(1, overdue_days // period + 1)`, then `due_date + k * period`. Added an optional `today` parameter for testing. | Same idea, written with a `threshold = max(due_date, today)` variable and `k = (threshold - due_date).days // step + 1`. Also added an optional `today` parameter. |
| **What was useful** | It used math instead of a loop, so it works even if a task is months late. It pointed out that `int()` would round negative numbers the wrong way and floor division (`//`) is needed. It also mentioned that completing the same task twice would create two copies. | The "threshold" version is easier to read. It explained clearly why `today + 7` is wrong: it makes a Saturday task drift to whatever day you finished it. It also raised an error for unknown frequencies instead of failing silently. |
| **Problems noticed** | One row in its example table didn't make sense ("Thu 10-17 +30 days late", but Oct 17 is a Saturday). It also returns `None` for unknown frequencies, so a typo like "weekyl" would silently stop the task from repeating. | Its examples mixed up dates (it said "today is Saturday Oct 17" and then used "completed Mon Oct 19"). Raising an error inside `next_occurrence()` would crash the app when someone marks a task done, which is the wrong place to catch a typo. |
| **Decision** | Used: the optional `today` parameter, and returning `None` for one-off tasks | Used: the `threshold` structure, because it's easier to read |

**Which approach did you use in your final implementation and why?**

I combined them. The core math is the same in both answers. I used Haiku's version with the `threshold` variable because a person can read it and understand it right away. I kept returning `None` for "once" tasks like Sonnet did, instead of raising an error. The UI only offers once, daily, or weekly anyway, so there's no typo to catch at that point. I also took the optional `today` parameter from both, which made it easy to write tests for "finished 2 days late" and "finished a month late" without faking the clock.

The biggest win was that both answers showed my original code had a bug. I was using `max(due_date, today) + 7 days`, which moved a Saturday task to Monday if I finished it on Monday. Now a Saturday task stays on Saturdays, and there are three tests to prove it.
