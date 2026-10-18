# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML has four classes with simple "has-a" relationships: an **Owner** has many **Pets**, each **Pet** has many **Tasks**, and a **Scheduler** works on behalf of one Owner to build the day's plan.

- **Task**: a single care activity. It holds what needs to happen (title, category), how long it takes, its priority, an optional preferred time, how often it repeats (once/daily/weekly), its due date, which pet it is for, and whether it's done. It can mark itself complete, turn its priority into a number for sorting, and create its next occurrence if it repeats.
- **Pet**: basic pet info (name, species, age) plus the list of tasks that belong to it. It is responsible for adding and removing its own tasks.
- **Owner**: the person using the app. It stores how many minutes they have for pet care each day, their preferences, and their pets. It can add pets and gather every task across all pets into one list.
- **Scheduler**: the "brain". It takes an Owner and is responsible for all planning logic: sorting tasks by priority or time, filtering by pet or completion status, detecting time conflicts, choosing which tasks fit in the available time, and explaining why the plan looks the way it does.

I kept data (Owner, Pet, Task as dataclasses) separate from logic (Scheduler) so the scheduling rules live in one place and are easy to test.

**b. Design changes**

Yes. After drafting the skeleton, I asked my AI assistant to review `pawpal_system.py` for missing relationships and logic bottlenecks, and made four changes:

1. **`Pet.add_task()` now stamps `task.pet_name`.** The pet's name was stored on both Pet and Task, so the two could disagree (e.g., a task under Mochi labeled "Biscuit"). Letting the Pet set it keeps a single source of truth.
2. **Added `Scheduler.skipped`.** `generate_plan()` only returned chosen tasks, so `explain_plan()` had no way to say *why* something was left out. The scheduler now records skipped tasks so the explanation can cover both.
3. **Added `Pet.complete_task(title)`.** `Task.next_occurrence()` existed, but nothing called it, so recurring tasks would never come back. Completing a task through the Pet marks it done and adds the next daily/weekly copy to the pet's list.
4. **Task validates `priority` in `__post_init__`.** A value like "High" or "urgent" would silently get the wrong sort rank. Priority is now lowercased and must be low/medium/high.

One suggestion I considered but did **not** adopt: caching the result of `Owner.get_all_tasks()`. With only a few pets and tasks the cost of rebuilding the list is negligible, and a cache could return stale data after tasks are added or completed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
