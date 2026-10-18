# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
