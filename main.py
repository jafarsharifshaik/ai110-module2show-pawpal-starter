"""Terminal demo for PawPal+: sorting, filtering, conflicts, free slots, planning, recurrence, and saving."""

import sys
import tempfile
from pathlib import Path

from tabulate import tabulate

from pawpal_system import CATEGORY_EMOJI, PRIORITY_EMOJI, Owner, Pet, Scheduler, Task

# Only color the output in a real terminal, so piped/copied output stays clean.
USE_COLOR = sys.stdout.isatty()
COLORS = {"green": "32", "yellow": "33", "red": "31", "bold": "1"}


def color(text: str, name: str) -> str:
    """Wrap text in an ANSI color code (when printing to a terminal)."""
    return f"\033[{COLORS[name]}m{text}\033[0m" if USE_COLOR else text


def heading(title: str) -> None:
    print(f"\n{color(title, 'bold')}")


def show(tasks: list[Task]) -> None:
    """Print tasks as a table with emojis for the category and priority, and a colored status."""
    rows = [
        [
            t.time or "anytime",
            f"{CATEGORY_EMOJI.get(t.category, '📝')} {t.title}",
            t.pet_name,
            t.duration_minutes,
            f"{PRIORITY_EMOJI[t.priority]} {t.priority}",
            t.due_date.strftime("%a %b %d"),
            color("✔ done", "green") if t.completed else color("○ open", "yellow"),
        ]
        for t in tasks
    ]
    headers = ["Time", "Task", "Pet", "Min", "Priority", "Due", "Status"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    biscuit = Pet("Biscuit", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Added deliberately out of time order to show sorting.
    mochi.add_task(Task("Evening walk", 25, "medium", category="walk", time="18:00", frequency="daily"))
    biscuit.add_task(Task("Thyroid meds", 5, "high", category="meds", time="20:00", frequency="daily"))
    mochi.add_task(Task("Bath and brush", 40, "low", category="grooming"))
    biscuit.add_task(Task("Laser pointer play", 15, "medium", category="enrichment", time="19:30"))
    mochi.add_task(Task("Morning walk", 30, "high", category="walk", time="07:30", frequency="daily"))
    # Same start time as Mochi's morning walk (different pets), to show conflict detection.
    biscuit.add_task(Task("Breakfast", 10, "high", category="feeding", time="07:30", frequency="daily"))
    # Same start time as Mochi's evening walk (same pet).
    mochi.add_task(Task("Flea treatment", 5, "medium", category="meds", time="18:00", frequency="weekly"))

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    heading("1. Sorted by time")
    show(scheduler.sort_by_time(all_tasks))

    heading("2. Sorted by priority, then time")
    show(scheduler.sort_by_priority_then_time(all_tasks))

    heading("3. Filtered: Biscuit only")
    show(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit")))

    heading("4. Conflict check")
    for warning in scheduler.detect_conflicts(all_tasks):
        print(color(f"  ⚠️  {warning}", "red"))

    heading("5. Next available slot")
    for minutes in (10, 40):
        print(f"  A {minutes}-minute task fits at: {scheduler.find_next_available_slot(minutes)}")

    heading("6. Today's schedule")
    plan = scheduler.generate_plan()
    show(plan)
    print(scheduler.explain_plan(plan))

    heading("7. Recurring task")
    walk = next(t for t in mochi.tasks if t.title == "Morning walk")
    follow_up = scheduler.mark_task_complete(walk)
    print(f"  Completed '{walk.title}' -> next one created for {follow_up.due_date:%a %b %d}")
    show(scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")))

    heading("8. Save and load")
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "data.json"
        owner.save_to_json(path)
        loaded = Owner.load_from_json(path)
        print(f"  Saved and reloaded {len(loaded.pets)} pets and {len(loaded.get_all_tasks())} tasks.")
        print(f"  Reloaded data matches the original: {loaded == owner}")


if __name__ == "__main__":
    main()
