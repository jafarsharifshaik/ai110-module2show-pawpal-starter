"""Terminal demo for PawPal+: exercises sorting, filtering, conflicts, scheduling, and recurrence."""

from pawpal_system import Owner, Pet, Scheduler, Task


def show(title: str, tasks: list[Task]) -> None:
    """Print a heading and one line per task."""
    print(f"\n{title}")
    print("-" * len(title))
    for t in tasks:
        status = "done" if t.completed else "open"
        print(f"  {t.time or 'anytime':>7}  {t.title:<20} {t.pet_name:<8} {t.priority:<6} due {t.due_date}  [{status}]")


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog", age=3)
    biscuit = Pet("Biscuit", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    # Added deliberately out of time order to show sorting.
    mochi.add_task(Task("Evening walk", 25, "medium", category="walk", time="18:00", frequency="daily"))
    biscuit.add_task(Task("Thyroid meds", 5, "high", category="meds", time="12:00", frequency="daily"))
    mochi.add_task(Task("Bath and brush", 40, "low", category="grooming"))
    biscuit.add_task(Task("Laser pointer play", 15, "medium", category="enrichment", time="19:30"))
    mochi.add_task(Task("Morning walk", 30, "high", category="walk", time="07:30", frequency="daily"))
    # Same start time as Mochi's morning walk (different pets), to show conflict detection.
    biscuit.add_task(Task("Breakfast", 10, "high", category="feeding", time="07:30", frequency="daily"))
    # Same start time as Mochi's evening walk (same pet).
    mochi.add_task(Task("Flea treatment", 5, "medium", category="meds", time="18:00", frequency="weekly"))

    scheduler = Scheduler(owner)

    show("Tasks as entered", owner.get_all_tasks())
    show("Sorted by time", scheduler.sort_by_time(owner.get_all_tasks()))
    show("Filtered: Biscuit only", scheduler.filter_tasks(pet_name="Biscuit"))

    print("\nConflict check")
    print("--------------")
    for warning in scheduler.detect_conflicts(owner.get_all_tasks()):
        print(f"  WARNING: {warning}")

    plan = scheduler.generate_plan()
    print("\nToday's Schedule")
    print("================")
    print(scheduler.explain_plan(plan))

    walk = next(t for t in mochi.tasks if t.title == "Morning walk")
    follow_up = scheduler.mark_task_complete(walk)
    print(f"\nCompleted '{walk.title}' -> next one created for {follow_up.due_date}")
    show("Filtered: completed tasks", scheduler.filter_tasks(completed=True))
    show("Filtered: Mochi's open tasks", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi", completed=False)))


if __name__ == "__main__":
    main()
