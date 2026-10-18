# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I went with four classes. An Owner has pets, each Pet has tasks, and a Scheduler looks at the owner's pets and tasks to make a plan for the day.

- **Task** is one thing that needs to get done, like a walk or giving meds. It stores the name, how long it takes, how important it is (low, medium, high), what time it should happen, whether it repeats daily or weekly, when it's due, which pet it's for, and whether it's done.
- **Pet** has the pet's name, species, and age, plus its list of tasks. You can add or remove tasks from a pet.
- **Owner** is the person using the app. It keeps track of their pets and how many minutes they have for pet care each day. It can also give you all the tasks for all the pets in one list.
- **Scheduler** is where the actual planning happens. It sorts tasks, filters them, checks if any of them clash, picks which ones fit in the day, and explains why.

I made Task, Pet, and Owner simple data classes and put all the planning logic in Scheduler. That way the rules are in one place and easier to test.

**b. Design changes**

Yes. After I wrote the skeleton, I asked AI to look over it for anything missing. It found a few problems, and I changed four things:

1. Each task stores its pet's name, but nothing made sure it was the right name. A task under Mochi could end up labeled "Biscuit." Now when you add a task to a pet, the pet fills in its own name.
2. The plan only listed the tasks that made it in, so there was no way to explain why something got left out. Now the scheduler keeps a list of skipped tasks too.
3. I had a method to make the next copy of a repeating task, but nothing ever used it, so daily tasks would never come back. I added a way to complete a task through the pet, which also creates the next one.
4. If someone typed "High" or "urgent" for priority, sorting would break. Now it lowercases the value and only accepts low, medium, or high.

AI also suggested saving the full task list instead of rebuilding it every time. I skipped that one. With only a few pets it doesn't really matter, and a saved list could get out of date when tasks change.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at four things:

1. **Time available:** the owner says how many minutes they have today, and the plan can't go over that.
2. **Priority:** high, medium, or low. High-priority tasks get picked first. If two tasks have the same priority, the shorter one goes first so more things fit.
3. **Due date:** only tasks due today (or overdue) go into today's plan. Finished tasks and tasks for later days are left out.
4. **Start time:** used to put the plan in order and to spot clashes.

I decided time and priority mattered most because that's the real problem for a busy owner. There isn't enough time for everything, so the important stuff like meds and feeding has to happen first. A missed play session is fine, but a missed dose of medicine isn't. The Owner class has a preferences field, but the scheduler doesn't use it yet. I left it out to keep the logic simple.

**b. Tradeoffs**

The main tradeoff is how the scheduler picks tasks. It starts with the most important ones and adds each task if there's still time left. It never goes back to rearrange things, so sometimes the day isn't packed as tightly as it could be. In my demo, the 40-minute bath gets skipped because the important tasks already used up the time. A smarter method might fit in a bit more, but it would be harder to explain, and the choices could seem random.

I think that's fine for a pet owner. The rule is simple: meds and feeding always come first. The app can also explain in one sentence why something was skipped. With only a few tasks a day, you don't lose much time.

Another tradeoff is that the scheduler only warns about clashes, it doesn't fix them. It checks whether two tasks overlap in time (not just whether they start at the same minute), but it doesn't move anything. Some overlaps are fine in real life, like feeding the cat right before taking the dog out, so I'd rather let the owner decide.

I also picked simple code over clever code for the conflict check. My first version used a trick to skip some comparisons. When I asked AI how to simplify it, it suggested just checking every pair of tasks. That's a little slower, but with a dozen tasks you'd never notice, and it's much easier to read, so I kept the simpler one.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code inside VS Code for pretty much every phase. I used it to brainstorm the classes, draw the UML, write the skeleton, fill in the logic, build the demo script, write tests, connect the Streamlit UI, and write documentation.

The most helpful prompts were the ones where I gave it the actual assignment step and asked it to go "step by step." That way it stopped after each step and I could check the work before moving on. Asking "what more can we add without making it too complicated?" was also really useful. It gave me a list of options with reasons, plus a list of things to skip, so I could pick instead of just accepting whatever it wrote.

**b. Judgment and verification**

During the design phase, the AI suggested leaving the task's start time and pet name out of the first skeleton, so I'd have something to "fix" later during the review step. I didn't go with that. I could already tell that conflict detection needs a start time, and a plan with two pets needs to show which pet each task is for. So I added them from the start. Later, when the AI reviewed the skeleton, it suggested saving the full task list instead of rebuilding it every time. I said no to that too, because with a few pets it doesn't matter, and a saved list could get out of date.

To check what the AI wrote, I ran `main.py` and read the output line by line to make sure the plan made sense (for example, that the bath was skipped because time ran out, not because of a bug). I also ran the tests after every change and tried the app myself. When something didn't look right, like tomorrow's task showing up before today's in the sorted list, we fixed the code instead of ignoring it.

**c. AI strategy**

- **Most effective features:** Agent mode was the biggest help, because it could edit several files at once (like `pawpal_system.py`, `app.py`, and the UML) and keep them in sync. It was also useful that it could run the code and the tests by itself and show me the results, instead of me copying and pasting. Starting in plan mode helped too, because I saw the whole plan before any files changed.
- **A suggestion I changed:** the start time and pet name example above. I also changed how commits were made. I wanted the commits to be under my own name only, so I told it not to add itself as a co-author.
- **Organizing by phase:** I mostly worked in one long chat, but I gave it one phase at a time and had it finish and commit each phase before starting the next. That kept things organized because each phase had its own commit and a clear "done" point. If I did it again, I'd use a fresh chat for each phase like the assignment suggests. The context would be cleaner, and the AI wouldn't carry over assumptions from earlier steps.
- **Being the lead architect:** The AI can write a lot of code fast, but it doesn't know what matters to the user unless I tell it. My job was to make the decisions: which features are worth it, which suggestions to skip, when to keep things simple, and whether the output actually makes sense. When I gave clear direction and checked each step, the results were good.

---

## 4. Testing and Verification

**a. What you tested**

I have 26 tests that cover:

- **Sorting:** tasks come out in time order, tasks with no time go last, "9:00" comes before "10:00", and earlier dates come first.
- **Filtering:** by pet, by done or not done, and a pet with no tasks.
- **Recurring tasks:** a daily task comes back tomorrow, a weekly one in 7 days, one-time tasks don't repeat, and an overdue daily task comes back tomorrow instead of on a day that already passed.
- **Conflicts:** tasks at the same time get flagged (same pet or different pets), and so do partial overlaps. Back-to-back tasks and tasks on different days don't get flagged.
- **The daily plan:** it stays within the time limit, skips what doesn't fit, leaves out finished and future tasks, and works when there are no tasks or zero free minutes.

These tests matter because these are the features a pet owner actually depends on. If sorting is wrong, the plan is confusing. If recurring tasks break, a daily med could just disappear after one day. The edge cases are where bugs usually hide. For example, a small mistake in the overlap check could make back-to-back tasks (08:00-08:30 and 08:30) count as a clash, and "9:00" vs "10:00" would sort wrong as plain text.

**b. Confidence**

I'd say 4 out of 5. All the tests pass, and they cover the main features plus the tricky cases I could think of. I'm not at 5 because the tests don't cover the Streamlit app, only the logic behind it.

If I had more time, I'd test:

- Bad input, like a time typed as "25:99" or a negative duration. Right now that would cause an error instead of a friendly message.
- Two tasks with the same name for the same pet, to make sure completing one doesn't mark the other.
- A weekly task completed several days early or late.
- What happens around midnight, like a task at 23:45 that runs past 00:00.

---

## 5. Reflection

**a. What went well**

I'm happiest with how simple the design stayed. It's still just the four classes from my first UML, and all the planning logic is in one place (the Scheduler). Because of that, adding sorting, filtering, recurring tasks, and conflict warnings later didn't mean rewriting anything. I also like that the app explains itself. It doesn't just skip a task, it tells you why.

**b. What you would improve**

- Actually use the owner's preferences, like "walks in the morning," when building the plan.
- Let the owner edit or delete a task in the app. Right now you can only add tasks and mark them done.
- Save the data to a file so it doesn't disappear when you close the browser.
- Have the scheduler suggest a new time when there's a clash, instead of only warning about it.

**c. Key takeaway**

Designing first really paid off. Spending time on the UML and the skeleton before writing any logic meant the code had a clear shape, and the AI had something solid to build on. The other big lesson is that I have to stay in charge when working with AI. It's fast and usually right, but it will happily add things I don't need. I had to decide what to keep, check that the output made sense, and push back when something didn't fit the design.
