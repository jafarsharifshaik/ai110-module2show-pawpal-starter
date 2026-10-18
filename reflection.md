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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The main tradeoff is how the scheduler picks tasks. It starts with the most important ones and adds each task if there's still time left. It never goes back to rearrange things, so sometimes the day isn't packed as tightly as it could be. In my demo, the 40-minute bath gets skipped because the important tasks already used up the time. A smarter method might fit in a bit more, but it would be harder to explain, and the choices could seem random.

I think that's fine for a pet owner. The rule is simple: meds and feeding always come first. The app can also explain in one sentence why something was skipped. With only a few tasks a day, you don't lose much time.

Another tradeoff is that the scheduler only warns about clashes, it doesn't fix them. It checks whether two tasks overlap in time (not just whether they start at the same minute), but it doesn't move anything. Some overlaps are fine in real life, like feeding the cat right before taking the dog out, so I'd rather let the owner decide.

I also picked simple code over clever code for the conflict check. My first version used a trick to skip some comparisons. When I asked AI how to simplify it, it suggested just checking every pair of tasks. That's a little slower, but with a dozen tasks you'd never notice, and it's much easier to read, so I kept the simpler one.

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
