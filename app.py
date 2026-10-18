from datetime import date
from pathlib import Path

import streamlit as st

from pawpal_system import CATEGORY_EMOJI, PRIORITY_EMOJI, Owner, Pet, Scheduler, Task

DATA_FILE = Path(__file__).parent / "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on time, priority, and schedule.")



def load_owner() -> Owner:
    """Load saved data from data.json, or start fresh if there isn't any (or it's unreadable)."""
    if DATA_FILE.exists():
        try:
            return Owner.load_from_json(DATA_FILE)
        except (ValueError, KeyError, TypeError):
            st.warning("Couldn't read the saved data in data.json, so starting fresh.")
    return Owner("Jordan", available_minutes=60)


# Streamlit reruns this script on every interaction, so keep the Owner in session_state.
# It's loaded once per browser session (from data.json if it exists); later reruns reuse it.
if "owner" not in st.session_state:
    st.session_state.owner = load_owner()

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn tasks into rows for st.table / st.dataframe."""
    return [
        {
            "Time": t.time or "anytime",
            "Task": f"{CATEGORY_EMOJI.get(t.category, '📝')} {t.title}",
            "Pet": t.pet_name,
            "Minutes": t.duration_minutes,
            "Priority": f"{PRIORITY_EMOJI[t.priority]} {t.priority}",
            "Repeats": t.frequency,
            "Due": t.due_date.strftime("%a %b %d"),
            "Status": "✅ done" if t.completed else "⏳ to do",
        }
        for t in tasks
    ]


def show_conflicts(warnings: list[str]) -> None:
    """Show time clashes as one clear warning box with a tip on what to do."""
    if not warnings:
        return
    noun = "clash" if len(warnings) == 1 else "clashes"
    lines = "\n".join(f"- {w}" for w in warnings)
    st.warning(
        f"**⚠️ {len(warnings)} time {noun} today**\n\n{lines}\n\n"
        "If you're doing these yourself, try moving one to a different time. "
        "If someone else can handle one, it's fine to leave it."
    )


with st.sidebar:
    st.markdown("### 💾 Saved data")
    st.caption("Your pets and tasks are saved to data.json automatically after every change.")
    if st.button("🗑️ Start over"):
        DATA_FILE.unlink(missing_ok=True)
        st.session_state.owner = Owner("Jordan", available_minutes=60)
        st.rerun()

# --- Owner -----------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Minutes available today", min_value=0, max_value=1440, value=owner.available_minutes, step=5
        )
    )

st.divider()

# --- Pets ------------------------------------------------------------------
st.subheader("Pets")
with st.form("add_pet", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
    if st.form_submit_button("Add pet"):
        name = pet_name.strip()
        if not name:
            st.error("Please enter a pet name.")
        elif any(p.name == name for p in owner.pets):
            st.error(f"You already have a pet named {name}.")
        else:
            owner.add_pet(Pet(name, species, age=int(age)))
            st.success(f"Added {name}.")

if owner.pets:
    st.write(", ".join(f"**{p.name}** ({p.species}, {p.age} yr)" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Tasks -----------------------------------------------------------------
st.subheader("Tasks")
if not owner.pets:
    st.caption("Add a pet first, then you can give it tasks.")
else:
    with st.form("add_task", clear_on_submit=True):
        pet_choice = st.selectbox("For pet", [p.name for p in owner.pets])
        col1, col2, col3 = st.columns(3)
        with col1:
            task_title = st.text_input("Task title", value="Morning walk")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox(
                "Category", ["walk", "feeding", "meds", "grooming", "enrichment", "general"]
            )
        with col2:
            start = st.time_input("Start time (optional)", value=None, step=900)
        with col3:
            frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        auto_time = st.checkbox("Pick the next free time for me (ignores the start time above)")
        if st.form_submit_button("Add task"):
            if auto_time:
                slot = scheduler.find_next_available_slot(int(duration))
                start_text = slot or ""
            else:
                slot = None
                start_text = start.strftime("%H:%M") if start else ""
            if not task_title.strip():
                st.error("Please enter a task title.")
            elif auto_time and slot is None:
                st.error(f"There's no free {int(duration)}-minute gap between 07:00 and 21:00 today.")
            else:
                pet = next(p for p in owner.pets if p.name == pet_choice)
                pet.add_task(
                    Task(
                        task_title.strip(),
                        int(duration),
                        priority,
                        category=category,
                        time=start_text,
                        frequency=frequency,
                    )
                )
                when = f" at {start_text}" if start_text else ""
                st.success(f"Added '{task_title.strip()}' for {pet_choice}{when}.")

    col1, col2, col3 = st.columns(3)
    with col1:
        show_pet = st.selectbox("Show tasks for", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        show_status = st.selectbox("Status", ["All", "Not done", "Done"])
    with col3:
        sort_choice = st.selectbox("Sort by", ["Time", "Priority, then time"])
    visible = scheduler.filter_tasks(
        pet_name=None if show_pet == "All pets" else show_pet,
        completed={"All": None, "Not done": False, "Done": True}[show_status],
    )
    if visible:
        if sort_choice == "Time":
            st.table(task_rows(scheduler.sort_by_time(visible)))
            st.caption("Sorted by date, then by time. Tasks with no set time are listed last.")
        else:
            st.table(task_rows(scheduler.sort_by_priority_then_time(visible)))
            st.caption("🔴 High first, then 🟡 medium, then 🟢 low. Each group is in time order.")
    elif owner.get_all_tasks():
        st.info("No tasks match these filters.")
    else:
        st.info("No tasks yet. Add one above.")

    # Warn about clashes as soon as they exist, not only after generating a plan.
    due_today = [t for t in scheduler.filter_tasks(completed=False) if t.due_date <= date.today()]
    show_conflicts(scheduler.detect_conflicts(due_today))

    open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if open_tasks:
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            labels = [f"{t.pet_name}: {t.title} (due {t.due_date.isoformat()})" for t in open_tasks]
            picked = st.selectbox("Mark a task done", range(len(open_tasks)), format_func=labels.__getitem__)
        with col2:
            if st.button("Mark done"):
                scheduler.mark_task_complete(open_tasks[picked])
                owner.save_to_json(DATA_FILE)  # st.rerun() stops the script, so save first
                st.rerun()

st.divider()

# --- Schedule --------------------------------------------------------------
st.subheader("Today's Schedule")
if st.button("Generate schedule", type="primary"):
    plan = scheduler.generate_plan()
    if not plan and not scheduler.skipped:
        st.info("No tasks are due today.")
    else:
        used = sum(t.duration_minutes for t in plan)
        col1, col2, col3 = st.columns(3)
        col1.metric("Tasks planned", len(plan))
        col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
        col3.metric("Skipped", len(scheduler.skipped))

        if plan:
            st.success(f"Here's your plan for today, {owner.name}. Most important tasks were picked first.")
            st.table(
                [
                    {k: row[k] for k in ("Time", "Task", "Pet", "Minutes", "Priority")}
                    for row in task_rows(plan)
                ]
            )
        show_conflicts(scheduler.detect_conflicts(plan))
        for t in scheduler.skipped:
            st.info(
                f"Skipped **{t.title}** ({t.pet_name}): it needs {t.duration_minutes} min, "
                f"but only {owner.available_minutes - used} min were left after more important tasks."
            )
        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan(plan))

# Save after every run so pets and tasks survive closing the app.
owner.save_to_json(DATA_FILE)
