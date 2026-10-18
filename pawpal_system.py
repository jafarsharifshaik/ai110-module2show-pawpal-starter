"""PawPal+ logic layer: the backend classes behind the Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


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
        pass

    def priority_rank(self) -> int:
        """Return a number for sorting (higher = more important)."""
        pass

    def next_occurrence(self) -> Task | None:
        """Return the next copy of a recurring task, or None if it doesn't repeat."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and stamp it with this pet's name."""
        pass

    def remove_task(self, title: str) -> None:
        """Remove a task by its title."""
        pass

    def complete_task(self, title: str) -> None:
        """Mark a task done and, if it recurs, add its next occurrence."""
        pass


@dataclass
class Owner:
    """The pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int = 60
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across all of the owner's pets."""
        pass


class Scheduler:
    """Builds a daily care plan for an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner
        self.skipped: list[Task] = []  # tasks left out of the last plan, for explain_plan

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit within the owner's available time; record the rest in skipped."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by their preferred start time."""
        pass

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return tasks matching the given pet and/or completion status."""
        pass

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks scheduled at the same time."""
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable explanation of why each task was chosen or skipped."""
        pass
