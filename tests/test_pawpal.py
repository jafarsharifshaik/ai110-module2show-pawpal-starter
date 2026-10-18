"""Tests for core PawPal+ behaviors: tasks, sorting, filtering, recurrence, conflicts, and planning."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date.today()


def make_owner(minutes: int = 60) -> tuple[Owner, Pet, Pet]:
    """An owner with two pets and no tasks yet."""
    owner = Owner("Jordan", available_minutes=minutes)
    mochi, biscuit = Pet("Mochi", "dog"), Pet("Biscuit", "cat")
    owner.add_pet(mochi)
    owner.add_pet(biscuit)
    return owner, mochi, biscuit


# --- Basic task and pet behavior ---------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_name == "Mochi"


def test_priority_is_case_insensitive_and_validated():
    assert Task("Walk", 10, " High ").priority == "high"
    with pytest.raises(ValueError):
        Task("Walk", 10, "urgent")


def test_owner_get_all_tasks_combines_every_pet():
    owner, mochi, biscuit = make_owner()
    mochi.add_task(Task("Walk", 30))
    biscuit.add_task(Task("Feed", 10))

    assert {t.title for t in owner.get_all_tasks()} == {"Walk", "Feed"}


# --- Sorting -----------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    owner, mochi, biscuit = make_owner()
    mochi.add_task(Task("Evening walk", 20, time="18:00"))
    biscuit.add_task(Task("Lunch", 10, time="12:00"))
    mochi.add_task(Task("Morning walk", 30, time="07:30"))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.time for t in ordered] == ["07:30", "12:00", "18:00"]


def test_sort_by_time_puts_untimed_tasks_last():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Brush", 10))
    mochi.add_task(Task("Walk", 30, time="09:00"))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Walk", "Brush"]


def test_sort_by_time_handles_single_digit_hours():
    # "9:00" should come before "10:00", which a plain string sort would get wrong.
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Late", 10, time="10:00"))
    mochi.add_task(Task("Early", 10, time="9:00"))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Early", "Late"]


def test_sort_by_time_orders_by_date_first():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Tomorrow early", 10, time="07:00", due_date=TODAY + timedelta(days=1)))
    mochi.add_task(Task("Today late", 10, time="20:00"))

    ordered = Scheduler(owner).sort_by_time(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["Today late", "Tomorrow early"]


def test_sort_by_priority_high_first_shorter_wins_ties():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Low", 5, "low"))
    mochi.add_task(Task("High long", 30, "high"))
    mochi.add_task(Task("High short", 10, "high"))

    ordered = Scheduler(owner).sort_by_priority(owner.get_all_tasks())

    assert [t.title for t in ordered] == ["High short", "High long", "Low"]


# --- Filtering ---------------------------------------------------------------

def test_filter_by_pet_and_status():
    owner, mochi, biscuit = make_owner()
    mochi.add_task(Task("Walk", 30))
    biscuit.add_task(Task("Feed", 10))
    biscuit.add_task(Task("Play", 15, completed=True))
    scheduler = Scheduler(owner)

    assert [t.title for t in scheduler.filter_tasks(pet_name="Biscuit")] == ["Feed", "Play"]
    assert [t.title for t in scheduler.filter_tasks(completed=False)] == ["Walk", "Feed"]
    assert [t.title for t in scheduler.filter_tasks(pet_name="Biscuit", completed=True)] == ["Play"]


def test_filter_for_pet_with_no_tasks_is_empty():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Walk", 30))

    assert Scheduler(owner).filter_tasks(pet_name="Biscuit") == []


# --- Recurring tasks ---------------------------------------------------------

def test_completing_daily_task_creates_one_for_tomorrow():
    owner, mochi, _ = make_owner()
    walk = Task("Walk", 30, time="07:30", frequency="daily")
    mochi.add_task(walk)

    follow_up = Scheduler(owner).mark_task_complete(walk)

    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.due_date == TODAY + timedelta(days=1)
    assert follow_up.completed is False
    assert follow_up.time == "07:30" and follow_up.pet_name == "Mochi"
    assert len(mochi.tasks) == 2


def test_completing_weekly_task_creates_one_next_week():
    owner, mochi, _ = make_owner()
    flea = Task("Flea meds", 5, frequency="weekly")
    mochi.add_task(flea)

    follow_up = Scheduler(owner).mark_task_complete(flea)

    assert follow_up.due_date == TODAY + timedelta(weeks=1)


def test_completing_one_time_task_does_not_repeat():
    owner, mochi, _ = make_owner()
    vet = Task("Vet visit", 60)
    mochi.add_task(vet)

    assert Scheduler(owner).mark_task_complete(vet) is None
    assert len(mochi.tasks) == 1


def test_overdue_daily_task_comes_back_tomorrow_not_in_the_past():
    owner, mochi, _ = make_owner()
    old = Task("Walk", 30, frequency="daily", due_date=TODAY - timedelta(days=3))
    mochi.add_task(old)

    follow_up = Scheduler(owner).mark_task_complete(old)

    assert follow_up.due_date == TODAY + timedelta(days=1)


def test_pet_complete_task_by_title():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, frequency="daily"))

    pet.complete_task("Walk")

    assert [t.completed for t in pet.tasks] == [True, False]
    with pytest.raises(ValueError):
        pet.complete_task("Nap")


# --- Conflict detection ------------------------------------------------------

def test_conflict_flagged_for_same_time_different_pets():
    owner, mochi, biscuit = make_owner()
    mochi.add_task(Task("Walk", 30, time="07:30"))
    biscuit.add_task(Task("Breakfast", 10, time="07:30"))

    warnings = Scheduler(owner).detect_conflicts(owner.get_all_tasks())

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Breakfast" in warnings[0]


def test_conflict_flagged_for_same_time_same_pet():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Evening walk", 25, time="18:00"))
    mochi.add_task(Task("Flea meds", 5, time="18:00"))

    assert len(Scheduler(owner).detect_conflicts(owner.get_all_tasks())) == 1


def test_conflict_flagged_for_partial_overlap():
    owner, mochi, biscuit = make_owner()
    mochi.add_task(Task("Walk", 30, time="08:00"))  # 08:00-08:30
    biscuit.add_task(Task("Feed", 10, time="08:15"))

    assert len(Scheduler(owner).detect_conflicts(owner.get_all_tasks())) == 1


def test_back_to_back_tasks_are_not_a_conflict():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Walk", 30, time="08:00"))  # ends at 08:30
    mochi.add_task(Task("Feed", 10, time="08:30"))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_same_time_on_different_days_is_not_a_conflict():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Walk", 30, time="08:00"))
    mochi.add_task(Task("Walk", 30, time="08:00", due_date=TODAY + timedelta(days=1)))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


def test_untimed_tasks_never_conflict():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Brush", 10))
    mochi.add_task(Task("Play", 10))

    assert Scheduler(owner).detect_conflicts(owner.get_all_tasks()) == []


# --- Daily plan --------------------------------------------------------------

def test_plan_fits_time_budget_and_skips_what_doesnt_fit():
    owner, mochi, biscuit = make_owner(minutes=45)
    mochi.add_task(Task("Walk", 30, "high", time="07:30"))
    biscuit.add_task(Task("Feed", 10, "high", time="08:00"))
    mochi.add_task(Task("Bath", 40, "low"))
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    assert [t.title for t in plan] == ["Walk", "Feed"]
    assert sum(t.duration_minutes for t in plan) <= owner.available_minutes
    assert [t.title for t in scheduler.skipped] == ["Bath"]
    assert "Skipped" in scheduler.explain_plan(plan)


def test_plan_leaves_out_completed_and_future_tasks():
    owner, mochi, _ = make_owner()
    mochi.add_task(Task("Done already", 10, completed=True))
    mochi.add_task(Task("Next week", 10, due_date=TODAY + timedelta(weeks=1)))
    mochi.add_task(Task("Overdue", 10, due_date=TODAY - timedelta(days=1)))

    plan = Scheduler(owner).generate_plan()

    assert [t.title for t in plan] == ["Overdue"]


def test_plan_with_no_tasks_is_empty():
    owner = Owner("Jordan")
    scheduler = Scheduler(owner)

    plan = scheduler.generate_plan()

    assert plan == []
    assert scheduler.explain_plan(plan) == "No tasks are due today."


def test_zero_minutes_available_skips_everything():
    owner, mochi, _ = make_owner(minutes=0)
    mochi.add_task(Task("Walk", 30))
    scheduler = Scheduler(owner)

    assert scheduler.generate_plan() == []
    assert len(scheduler.skipped) == 1
