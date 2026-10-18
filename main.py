"""Terminal demo for PawPal+: builds an owner with two pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)

    mochi = Pet("Mochi", "dog", age=3)
    biscuit = Pet("Biscuit", "cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(biscuit)

    mochi.add_task(Task("Morning walk", 30, "high", category="walk", time="07:30", frequency="daily"))
    mochi.add_task(Task("Evening walk", 25, "medium", category="walk", time="18:00", frequency="daily"))
    mochi.add_task(Task("Bath and brush", 40, "low", category="grooming"))
    biscuit.add_task(Task("Breakfast", 10, "high", category="feeding", time="07:45", frequency="daily"))
    biscuit.add_task(Task("Thyroid meds", 5, "high", category="meds", time="12:00", frequency="daily"))
    biscuit.add_task(Task("Laser pointer play", 15, "medium", category="enrichment", time="19:30"))

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("Today's Schedule")
    print("=" * 16)
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
