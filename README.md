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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All scheduling logic lives in the `Scheduler` class in `pawpal_system.py`. It always reads tasks through `Owner.get_all_tasks()`, so every feature works across all of an owner's pets.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sort_by_time` uses `sorted()` with a lambda key of (due date, has no time?, minutes after midnight), so tasks appear in clock order with "anytime" tasks last for each day. `sort_by_priority` ranks high → low (via `Task.priority_rank()`), breaking ties with the shorter task. |
| Filtering | `Scheduler.filter_tasks(pet_name=None, completed=None)` | Filter by pet, by completion status, or both. Passing `None` means "don't filter on that". |
| Daily plan | `Scheduler.generate_plan()`, `Scheduler.explain_plan()` | Greedy: takes open tasks due today or earlier, highest priority first, keeping each one that still fits in `Owner.available_minutes`. Tasks that don't fit go to `Scheduler.skipped`, and `explain_plan()` says why each task was chosen or skipped. |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags any two timed tasks on the same day whose windows overlap (start + duration), for the same pet or different pets. Returns warning strings instead of raising, so the app never crashes on a clash. |
| Recurring tasks | `Scheduler.mark_task_complete()`, `Pet.complete_task()`, `Task.next_occurrence()` | Completing a `daily` or `weekly` task automatically adds a fresh copy due `today + timedelta(days=1)` or `today + timedelta(weeks=1)`. One-off tasks just stay completed. |
| Input safety | `Task.__post_init__()` | Priority is lowercased and must be low/medium/high, so values like "High" sort correctly. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
