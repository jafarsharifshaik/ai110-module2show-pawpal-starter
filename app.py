import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care for the day based on time, priority, and schedule.")

# Streamlit reruns this script on every interaction, so keep the Owner in session_state.
# It's created once per browser session; later reruns reuse the same object (and its pets/tasks).
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", available_minutes=60)

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks: list[Task]) -> list[dict]:
    """Turn tasks into rows for st.table / st.dataframe."""
    return [
        {
            "Time": t.time or "anytime",
            "Task": t.title,
            "Pet": t.pet_name,
            "Minutes": t.duration_minutes,
            "Priority": t.priority,
            "Category": t.category,
            "Repeats": t.frequency,
            "Due": t.due_date.isoformat(),
            "Done": "✅" if t.completed else "",
        }
        for t in tasks
    ]


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
        if st.form_submit_button("Add task"):
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                pet = next(p for p in owner.pets if p.name == pet_choice)
                pet.add_task(
                    Task(
                        task_title.strip(),
                        int(duration),
                        priority,
                        category=category,
                        time=start.strftime("%H:%M") if start else "",
                        frequency=frequency,
                    )
                )
                st.success(f"Added '{task_title.strip()}' for {pet_choice}.")

    show_pet = st.selectbox("Show tasks for", ["All pets"] + [p.name for p in owner.pets])
    visible = scheduler.filter_tasks(pet_name=None if show_pet == "All pets" else show_pet)
    if visible:
        st.table(task_rows(scheduler.sort_by_time(visible)))
    else:
        st.info("No tasks yet. Add one above.")

    open_tasks = scheduler.filter_tasks(completed=False)
    if open_tasks:
        col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
        with col1:
            labels = [f"{t.pet_name}: {t.title} (due {t.due_date.isoformat()})" for t in open_tasks]
            picked = st.selectbox("Mark a task done", range(len(open_tasks)), format_func=labels.__getitem__)
        with col2:
            if st.button("Mark done"):
                scheduler.mark_task_complete(open_tasks[picked])
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
        st.success(f"Planned {len(plan)} task(s), using {used} of {owner.available_minutes} minutes.")
        if plan:
            st.table(task_rows(plan))
        for warning in scheduler.detect_conflicts(plan):
            st.warning(f"Time conflict: {warning}")
        for t in scheduler.skipped:
            st.info(f"Skipped **{t.title}** ({t.pet_name}): needs {t.duration_minutes} min, not enough time left.")
        with st.expander("Why this plan?"):
            st.text(scheduler.explain_plan(plan))
