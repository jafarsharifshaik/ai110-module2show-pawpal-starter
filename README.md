# 🐾 PawPal+

PawPal+ is a Streamlit app that helps a busy pet owner plan the day's pet care. You add your pets and their tasks (walks, feeding, meds, grooming, play), tell it how much time you have, and it builds a daily plan. It puts the most important tasks first, warns you when two tasks clash, and explains why it picked what it did.

## ✨ Features

- **Multiple pets:** one owner can have several pets, and every feature works across all of them.
- **Daily plan within your free time:** the most important tasks get picked first, and anything that doesn't fit in your available minutes is skipped (with a reason).
- **Sorting by time:** tasks are listed by date and then by time of day. Tasks with no set time go at the end.
- **Sorting by priority:** high priority comes first, and the shorter task wins a tie, so more tasks fit in the day.
- **Filtering:** see tasks for one pet, only the ones that still need doing, only finished ones, or a mix.
- **Conflict warnings:** if two tasks overlap in time (same pet or different pets), the app shows a warning instead of crashing.
- **Daily and weekly recurrence:** when you finish a repeating task, the next one is added automatically (tomorrow for daily, in 7 days for weekly).
- **Plan explanation:** a plain-English summary of why each task was chosen or skipped.
- **Input check:** priority must be low, medium, or high, so a typo can't break the sorting.

## 🚀 Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run it

```bash
streamlit run app.py   # the web app
python main.py         # terminal demo
python -m pytest       # tests
```

## 🏗️ Architecture

The code is split into a logic layer (`pawpal_system.py`) and a UI (`app.py`). `Owner`, `Pet`, and `Task` hold the data, and `Scheduler` does all of the planning. The source for this diagram is in [`diagrams/uml_final.mmd`](diagrams/uml_final.mmd).

```mermaid
classDiagram
    %% PawPal+ final UML, matching pawpal_system.py

    class Owner {
        +str name
        +int available_minutes
        +list~str~ preferences
        +list~Pet~ pets
        +add_pet(pet: Pet) None
        +get_all_tasks() list~Task~
    }

    class Pet {
        +str name
        +str species
        +int age
        +list~Task~ tasks
        +add_task(task: Task) None
        +remove_task(title: str) None
        +complete_task(title: str) Task
    }

    class Task {
        +str title
        +int duration_minutes
        +str priority
        +str category
        +str time
        +str frequency
        +date due_date
        +str pet_name
        +bool completed
        +mark_complete() None
        +priority_rank() int
        +next_occurrence() Task
    }

    class Scheduler {
        +Owner owner
        +list~Task~ skipped
        +generate_plan() list~Task~
        +explain_plan(plan: list~Task~) str
        +sort_by_time(tasks: list~Task~) list~Task~
        +sort_by_priority(tasks: list~Task~) list~Task~
        +filter_tasks(pet_name: str, completed: bool) list~Task~
        +detect_conflicts(tasks: list~Task~) list~str~
        +mark_task_complete(task: Task) Task
    }

    Owner "1" *-- "*" Pet : owns
    Pet "1" *-- "*" Task : has
    Scheduler --> Owner : reads tasks via get_all_tasks()
    Scheduler ..> Task : sorts, filters, plans
    Task ..> Task : next_occurrence() creates
```

## 🖥️ Sample Output

Output from running `python main.py` (one owner, two pets, seven tasks added out of order, 90-minute daily budget). It shows sorting, filtering, conflict warnings, the generated plan, and a daily task recurring after it's completed:

```
Tasks as entered
----------------
    18:00  Evening walk         Mochi    medium due 2026-10-17  [open]
  anytime  Bath and brush       Mochi    low    due 2026-10-17  [open]
    07:30  Morning walk         Mochi    high   due 2026-10-17  [open]
    18:00  Flea treatment       Mochi    medium due 2026-10-17  [open]
    12:00  Thyroid meds         Biscuit  high   due 2026-10-17  [open]
    19:30  Laser pointer play   Biscuit  medium due 2026-10-17  [open]
    07:30  Breakfast            Biscuit  high   due 2026-10-17  [open]

Sorted by time
--------------
    07:30  Morning walk         Mochi    high   due 2026-10-17  [open]
    07:30  Breakfast            Biscuit  high   due 2026-10-17  [open]
    12:00  Thyroid meds         Biscuit  high   due 2026-10-17  [open]
    18:00  Evening walk         Mochi    medium due 2026-10-17  [open]
    18:00  Flea treatment       Mochi    medium due 2026-10-17  [open]
    19:30  Laser pointer play   Biscuit  medium due 2026-10-17  [open]
  anytime  Bath and brush       Mochi    low    due 2026-10-17  [open]

Filtered: Biscuit only
----------------------
    12:00  Thyroid meds         Biscuit  high   due 2026-10-17  [open]
    19:30  Laser pointer play   Biscuit  medium due 2026-10-17  [open]
    07:30  Breakfast            Biscuit  high   due 2026-10-17  [open]

Conflict check
--------------
  WARNING: 'Morning walk' (Mochi, 07:30-08:00) overlaps 'Breakfast' (Biscuit, 07:30-07:40)
  WARNING: 'Evening walk' (Mochi, 18:00-18:25) overlaps 'Flea treatment' (Mochi, 18:00-18:05)

Today's Schedule
================
Plan for Jordan: 90 of 90 minutes used.
    07:30  Breakfast (Biscuit), 10 min, chosen because it is high priority and fits the time budget
    07:30  Morning walk (Mochi), 30 min, chosen because it is high priority and fits the time budget
    12:00  Thyroid meds (Biscuit), 5 min, chosen because it is high priority and fits the time budget
    18:00  Flea treatment (Mochi), 5 min, chosen because it is medium priority and fits the time budget
    18:00  Evening walk (Mochi), 25 min, chosen because it is medium priority and fits the time budget
    19:30  Laser pointer play (Biscuit), 15 min, chosen because it is medium priority and fits the time budget
  Skipped  Bath and brush (Mochi): needs 40 min, only 0 min left after higher-priority tasks
  Warning: 'Breakfast' (Biscuit, 07:30-07:40) overlaps 'Morning walk' (Mochi, 07:30-08:00)
  Warning: 'Flea treatment' (Mochi, 18:00-18:05) overlaps 'Evening walk' (Mochi, 18:00-18:25)

Completed 'Morning walk' -> next one created for 2026-10-18

Filtered: completed tasks
-------------------------
    07:30  Morning walk         Mochi    high   due 2026-10-17  [done]

Filtered: Mochi's open tasks
----------------------------
    18:00  Evening walk         Mochi    medium due 2026-10-17  [open]
    18:00  Flea treatment       Mochi    medium due 2026-10-17  [open]
  anytime  Bath and brush       Mochi    low    due 2026-10-17  [open]
    07:30  Morning walk         Mochi    high   due 2026-10-18  [open]
```

## 🧪 Testing PawPal+

Run the tests from the project folder (with the virtual environment turned on):

```bash
python -m pytest
```

### What the tests cover

All tests are in `tests/test_pawpal.py` (26 tests):

- **Basics:** marking a task done, adding tasks to a pet, getting every pet's tasks from the owner, and making sure priority only accepts low, medium, or high.
- **Sorting:** tasks come back in time order, tasks with no time go last, "9:00" sorts before "10:00", earlier dates come first, and high priority comes before low.
- **Filtering:** by pet, by done or not done, both together, and a pet with no tasks.
- **Recurring tasks:** finishing a daily task adds one for tomorrow, a weekly task comes back in 7 days, one-time tasks don't repeat, and an overdue daily task comes back tomorrow instead of on a day that's already passed.
- **Conflicts:** two tasks at the exact same time (same pet or different pets) get flagged, and so do tasks that only partly overlap. Back-to-back tasks, tasks on different days, and tasks with no time are not flagged.
- **Daily plan:** the plan stays within the owner's free time, skips what doesn't fit, leaves out finished and future tasks, and works with no tasks or zero free minutes.

### Test results

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/jafarsharif.shaik/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collected 26 items

tests/test_pawpal.py ..........................                          [100%]

============================== 26 passed in 0.04s ==============================
```

### Confidence level: ⭐⭐⭐⭐ (4/5)

All 26 tests pass, and they cover the main features plus the tricky cases I could think of. I'm not giving it 5 stars because the tests only check the logic in `pawpal_system.py`, not the Streamlit app. Also, the scheduler doesn't check for bad input like a time typed as "25:99" or a negative duration.

## 📐 Smarter Scheduling

All the scheduling code is in the `Scheduler` class in `pawpal_system.py`. It gets tasks from `Owner.get_all_tasks()`, so everything works across all of the owner's pets, not just one.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Sorts tasks by date and then by time. Tasks with no set time go at the end of the day. Priority sorting puts high first, and if two tasks tie, the shorter one goes first. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Shows tasks for one pet, only done or not-done tasks, or both. |
| Daily plan | `Scheduler.generate_plan()`, `Scheduler.explain_plan()` | Starts with the most important tasks and adds each one if there's still time left in the day. Anything that doesn't fit gets skipped, and the explanation says why. |
| Conflict handling | `Scheduler.detect_conflicts()` | Warns when two tasks overlap in time, whether they're for the same pet or different pets. It just prints a warning and doesn't crash. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Pet.complete_task()`, `Task.next_occurrence()` | When you finish a daily task, a new one is added for tomorrow. A weekly task comes back in 7 days. One-time tasks just stay done. |
| Input check | `Task.__post_init__()` | Priority has to be low, medium, or high. Capital letters like "High" are fine. |

## 📸 Demo Walkthrough

### What you can do in the app

The app is one page with four sections, from top to bottom:

- **Owner:** set your name and how many minutes you have for pet care today.
- **Pets:** add a pet with a name, species, and age. The app won't let you add two pets with the same name.
- **Tasks:** add a task for a pet with a title, how long it takes, priority, category, an optional start time, and whether it repeats (once, daily, or weekly). Below the form is a table of tasks that you can filter by pet and by status (all, not done, done). The table is always sorted by date and time. You can also pick any open task and mark it done.
- **Today's Schedule:** press **Generate schedule** to get today's plan.

### Example workflow

1. Run `streamlit run app.py`. Set the owner name to **Jordan** and minutes available to **60**.
2. Add two pets: **Mochi** (dog) and **Biscuit** (cat).
3. Add tasks for Mochi: **Morning walk** (30 min, high, 07:30, daily), **Evening walk** (25 min, medium, 18:00), and **Bath** (40 min, low, no time).
4. Add a task for Biscuit: **Breakfast** (10 min, high, 07:30).
5. As soon as Breakfast is added, a yellow warning appears under the task table: *"1 time clash today: 'Morning walk' (Mochi, 07:30-08:00) overlaps 'Breakfast' (Biscuit, 07:30-07:40)"*. It also gives a tip to move one task or let someone else handle it.
6. Set the filters to **Mochi** and **Not done**. The table now shows only Mochi's three tasks, in time order, with the Bath (no set time) last.
7. Press **Generate schedule**. Three numbers appear at the top: **2 tasks planned**, **40 / 60 minutes used**, and **2 skipped**. The plan table lists Breakfast and Morning walk at 07:30. The clash warning shows up again, and blue notes explain that the Evening walk (25 min) and Bath (40 min) were skipped because only 20 minutes were left after the more important tasks.
8. Open **Why this plan?** to read a plain-English reason for every task.
9. Mark **Morning walk** as done. It shows ✅ in the table, and a new Morning walk due tomorrow is added automatically because it repeats daily.

### Scheduler behaviors shown

| Behavior | Where you see it |
|---|---|
| Sorting by time | The task table and the plan table are both in time order, with untimed tasks last. |
| Filtering | The "Show tasks for" and "Status" dropdowns above the task table. |
| Priority + time budget | High-priority tasks get picked first. Tasks that don't fit are listed as skipped, with how many minutes were left. |
| Conflict warnings | A yellow warning box under the task table and again with the plan. |
| Daily recurrence | Marking a daily task done adds the next one for tomorrow. |

### Sample CLI output

The same logic runs in the terminal with `python main.py`. Here's the schedule part of its output (the full output is in the Sample Output section above):

```
Today's Schedule
================
Plan for Jordan: 90 of 90 minutes used.
    07:30  Breakfast (Biscuit), 10 min, chosen because it is high priority and fits the time budget
    07:30  Morning walk (Mochi), 30 min, chosen because it is high priority and fits the time budget
    12:00  Thyroid meds (Biscuit), 5 min, chosen because it is high priority and fits the time budget
    18:00  Flea treatment (Mochi), 5 min, chosen because it is medium priority and fits the time budget
    18:00  Evening walk (Mochi), 25 min, chosen because it is medium priority and fits the time budget
    19:30  Laser pointer play (Biscuit), 15 min, chosen because it is medium priority and fits the time budget
  Skipped  Bath and brush (Mochi): needs 40 min, only 0 min left after higher-priority tasks
  Warning: 'Breakfast' (Biscuit, 07:30-07:40) overlaps 'Morning walk' (Mochi, 07:30-08:00)
  Warning: 'Flea treatment' (Mochi, 18:00-18:05) overlaps 'Evening walk' (Mochi, 18:00-18:25)

Completed 'Morning walk' -> next one created for 2026-10-18
```
