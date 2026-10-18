"""PawPal+ logic layer: the backend classes behind the Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}
RECURRENCE_STEPS = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _to_minutes(hhmm: str) -> int:
    """Convert an "HH:MM" string to minutes after midnight."""
    t = datetime.strptime(hhmm, "%H:%M")
    return t.hour * 60 + t.minute


def _to_hhmm(minutes: int) -> str:
    """Convert minutes after midnight back to "HH:MM"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    category: str = "general"  # walk, feeding, meds, grooming, enrichment...
    time: str = ""  # preferred start time, "HH:MM"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""
    completed: bool = False

    VALID_PRIORITIES = ("low", "medium", "high")

    def __post_init__(self) -> None:
        """Normalize priority so typos like "High" don't break sorting."""
        self.priority = self.priority.strip().lower()
        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(f"priority must be one of {self.VALID_PRIORITIES}, got {self.priority!r}")

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def priority_rank(self) -> int:
        """Return a number for sorting (higher = more important)."""
        return PRIORITY_RANKS[self.priority]

    def next_occurrence(self) -> Task | None:
        """Return the next copy of a recurring task, or None if it doesn't repeat."""
        step = RECURRENCE_STEPS.get(self.frequency)
        if step is None:
            return None
        return replace(self, due_date=self.due_date + step, completed=False)


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and stamp it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def complete_task(self, title: str) -> None:
        """Mark a task done and, if it recurs, add its next occurrence."""
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                follow_up = task.next_occurrence()
                if follow_up is not None:
                    self.tasks.append(follow_up)
                return
        raise ValueError(f"{self.name} has no open task titled {title!r}")


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.skipped: list[Task] = []  # tasks left out of the last plan, for explain_plan

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit within the owner's available time; record the rest in skipped."""
        today = date.today()
        due = [t for t in self.filter_tasks(completed=False) if t.due_date <= today]

        plan: list[Task] = []
        self.skipped = []
        minutes_left = self.owner.available_minutes
        # Greedy: take the most important tasks first while they still fit.
        for task in self.sort_by_priority(due):
            if task.duration_minutes <= minutes_left:
                plan.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped.append(task)
        return self.sort_by_time(plan)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority."""
        # Ties go to the shorter task, so more tasks fit in the day.
        return sorted(tasks, key=lambda t: (-t.priority_rank(), t.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by their preferred start time."""
        # Tasks without a time go last, since they can happen whenever.
        return sorted(tasks, key=lambda t: (t.time == "", _to_minutes(t.time) if t.time else 0))

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return tasks matching the given pet and/or completion status."""
        return [
            t
            for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks whose time windows overlap."""
        timed = self.sort_by_time([t for t in tasks if t.time])
        warnings = []
        for i, a in enumerate(timed):
            a_start = _to_minutes(a.time)
            a_end = a_start + a.duration_minutes
            for b in timed[i + 1:]:
                b_start = _to_minutes(b.time)
                if b_start >= a_end:
                    break  # sorted by start, so nothing later can overlap a
                warnings.append(
                    f"'{a.title}' ({a.pet_name}, {a.time}-{_to_hhmm(a_end)}) overlaps "
                    f"'{b.title}' ({b.pet_name}, {b.time}-{_to_hhmm(b_start + b.duration_minutes)})"
                )
        return warnings

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why each task was chosen or skipped."""
        if not plan and not self.skipped:
            return "No tasks are due today."

        used = sum(t.duration_minutes for t in plan)
        minutes_left = self.owner.available_minutes - used
        lines = [f"Plan for {self.owner.name}: {used} of {self.owner.available_minutes} minutes used."]

        for t in plan:
            when = t.time or "anytime"
            lines.append(
                f"  {when:>7}  {t.title} ({t.pet_name}), {t.duration_minutes} min, "
                f"chosen because it is {t.priority} priority and fits the time budget"
            )
        for t in self.skipped:
            lines.append(
                f"  Skipped  {t.title} ({t.pet_name}): needs {t.duration_minutes} min, "
                f"only {minutes_left} min left after higher-priority tasks"
            )
        for warning in self.detect_conflicts(plan):
            lines.append(f"  Warning: {warning}")
        return "\n".join(lines)
