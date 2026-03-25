import copy
import json
import os
import random
import time
from datetime import date, timedelta
from pathlib import Path

import openai
import streamlit as st
from dotenv import load_dotenv


st.set_page_config(
    page_title="Pasona Connect Tarot App Demo",
    page_icon="🔮",
    layout="centered",
)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


INITIAL_DECK = [
    {
        "title": "The Innovator",
        "emoji": "💡",
        "meaning": "A brilliant new idea will energize your work. Trust your sudden insights.",
        "reversed_meaning": "You're experiencing creative block. Step away and seek new inspiration.",
        "theme": "creativity",
    },
    {
        "title": "The Collaborator",
        "emoji": "🤝",
        "meaning": "Your greatest success this week will come from teamwork. Reach out and connect.",
        "reversed_meaning": "Teamwork is faltering. Address miscommunication or try working solo for a bit.",
        "theme": "relationships",
    },
    {
        "title": "The Focus Master",
        "emoji": "🎯",
        "meaning": "Eliminate distractions. Deep, focused work on a single task will yield great results.",
        "reversed_meaning": "Scattered attention is holding you back. Reassess your priorities.",
        "theme": "focus",
    },
    {
        "title": "The Communicator",
        "emoji": "📣",
        "meaning": "Speak up. Your voice needs to be heard in an important meeting or discussion.",
        "reversed_meaning": "Misunderstandings may arise. Listen carefully and clarify your message.",
        "theme": "communication",
    },
    {
        "title": "The Restful Achiever",
        "emoji": "🧘",
        "meaning": "Don't confuse activity with progress. Take a break; your best work will follow.",
        "reversed_meaning": "Restlessness or burnout is near. Prioritize self-care and boundaries.",
        "theme": "wellbeing",
    },
    {
        "title": "The Bold Leader",
        "emoji": "🦁",
        "meaning": "An opportunity to lead or take ownership of a project will present itself. Seize it.",
        "reversed_meaning": "Overconfidence or reluctance to lead may cause setbacks. Reflect before acting.",
        "theme": "leadership",
    },
    {
        "title": "The Student",
        "emoji": "📚",
        "meaning": "A skill you need to learn is holding you back. Dedicate time to learning it.",
        "reversed_meaning": "Avoiding growth or ignoring feedback will stall your progress.",
        "theme": "growth",
    },
    {
        "title": "The Finisher",
        "emoji": "🏁",
        "meaning": "Stop starting and start finishing. Push that lingering project across the finish line.",
        "reversed_meaning": "Procrastination or perfectionism is blocking completion. Let go and finish.",
        "theme": "execution",
    },
    {
        "title": "The Networker",
        "emoji": "🌐",
        "meaning": "The solution to your problem lies with someone you haven't met yet. Expand your network.",
        "reversed_meaning": "Networking efforts may feel forced or unproductive. Focus on genuine connections.",
        "theme": "opportunity",
    },
    {
        "title": "The Organizer",
        "emoji": "🧹",
        "meaning": "Clarity comes from order. Tidy your workspace, organize your files, and plan your week.",
        "reversed_meaning": "Disorganization is causing confusion. Take time to restore order.",
        "theme": "structure",
    },
]

SPREAD_LABELS = ["Past Influence", "Present Focus", "Future Potential"]
JOURNEY_STEPS = [
    "1. Check-in",
    "2. Draw",
    "3. Interpret",
    "4. Action Plan",
    "5. Wrap-up",
]
DATA_DIR = Path("data")
PROGRESS_FILE = DATA_DIR / "user_progress.json"


def initialize_app_state():
    if "deck" not in st.session_state:
        deck = copy.deepcopy(INITIAL_DECK)
        random.shuffle(deck)
        st.session_state.deck = deck
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    if "current_card_index" not in st.session_state:
        st.session_state.current_card_index = 0
    if "journey_step" not in st.session_state:
        st.session_state.journey_step = 0
    if "selected_seed_index" not in st.session_state:
        st.session_state.selected_seed_index = None
    if "guided_reading" not in st.session_state:
        st.session_state.guided_reading = None
    if "guided_inputs" not in st.session_state:
        st.session_state.guided_inputs = {
            "name": "",
            "energy": 3,
            "challenge": "",
            "goal": "Build momentum on an important project",
        }
    if "reading_saved" not in st.session_state:
        st.session_state.reading_saved = False


def reset_journey(reset_deck=False):
    if reset_deck:
        deck = copy.deepcopy(INITIAL_DECK)
        random.shuffle(deck)
        st.session_state.deck = deck
    st.session_state.journey_step = 0
    st.session_state.selected_seed_index = None
    st.session_state.guided_reading = None
    st.session_state.reading_saved = False


def toggle_theme():
    st.session_state.theme_mode = (
        "dark" if st.session_state.theme_mode == "light" else "light"
    )


def ensure_progress_store():
    DATA_DIR.mkdir(exist_ok=True)
    if not PROGRESS_FILE.exists():
        PROGRESS_FILE.write_text(json.dumps({"profiles": {}}, indent=2), encoding="utf-8")


def load_progress_store():
    ensure_progress_store()
    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"profiles": {}}


def save_progress_store(store):
    ensure_progress_store()
    PROGRESS_FILE.write_text(json.dumps(store, indent=2), encoding="utf-8")


def current_profile_key():
    name = st.session_state.guided_inputs["name"].strip()
    return name.lower() if name else "guest"


def current_profile_label():
    name = st.session_state.guided_inputs["name"].strip()
    return name if name else "Guest"


def get_profile_snapshot():
    store = load_progress_store()
    profiles = store.setdefault("profiles", {})
    profile = profiles.setdefault(
        current_profile_key(),
        {
            "display_name": current_profile_label(),
            "total_sessions": 0,
            "last_session_date": None,
            "streak": 0,
            "best_streak": 0,
            "theme_counts": {},
            "history": [],
        },
    )
    profile["display_name"] = current_profile_label()
    return store, profile


def update_streak(profile, session_day):
    previous = profile.get("last_session_date")
    if previous == session_day:
        return
    if previous:
        previous_date = date.fromisoformat(previous)
        current_date = date.fromisoformat(session_day)
        if previous_date == current_date - timedelta(days=1):
            profile["streak"] += 1
        else:
            profile["streak"] = 1
    else:
        profile["streak"] = 1
    profile["best_streak"] = max(profile["best_streak"], profile["streak"])
    profile["last_session_date"] = session_day


def save_current_session():
    if st.session_state.reading_saved or not st.session_state.guided_reading:
        return

    store, profile = get_profile_snapshot()
    reading = st.session_state.guided_reading
    session_day = date.today().isoformat()
    next_move = st.session_state.get("user_next_move", "").strip()

    profile["total_sessions"] += 1
    update_streak(profile, session_day)
    theme = reading["dominant_theme"]
    profile["theme_counts"][theme] = profile["theme_counts"].get(theme, 0) + 1
    profile["history"].insert(
        0,
        {
            "date": session_day,
            "goal": st.session_state.guided_inputs["goal"],
            "challenge": st.session_state.guided_inputs["challenge"],
            "dominant_theme": theme,
            "cards": [
                {
                    "title": card["title"],
                    "is_reversed": card["is_reversed"],
                    "position_label": card["position_label"],
                }
                for card in reading["cards"]
            ],
            "next_move": next_move or reading["action_plan"][0],
        },
    )
    profile["history"] = profile["history"][:10]
    save_progress_store(store)
    st.session_state.reading_saved = True


def render_progress_dashboard():
    _, profile = get_profile_snapshot()
    st.subheader("Your Progress", anchor=False)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Sessions", profile["total_sessions"])
    metric_cols[1].metric("Current streak", profile["streak"])
    metric_cols[2].metric("Best streak", profile["best_streak"])

    if profile["theme_counts"]:
        top_theme = max(profile["theme_counts"], key=profile["theme_counts"].get)
        st.caption(f"Most common theme so far: {top_theme.title()}")

    recent = profile["history"][:3]
    if recent:
        st.write("Recent sessions")
        for item in recent:
            st.markdown(
                f"- {item['date']}: {item['dominant_theme'].title()} while working on {item['goal']}"
            )


def make_card_snapshot(card, reversed_state, position_label, card_number):
    return {
        "title": card["title"],
        "emoji": card["emoji"],
        "meaning": card["meaning"],
        "reversed_meaning": card["reversed_meaning"],
        "theme": card["theme"],
        "is_reversed": reversed_state,
        "position_label": position_label,
        "card_number": card_number,
        "active_meaning": card["reversed_meaning"] if reversed_state else card["meaning"],
    }


def build_guided_reading(seed_index):
    cards = []
    for offset, label in enumerate(SPREAD_LABELS):
        card_index = (seed_index + offset) % len(st.session_state.deck)
        card = st.session_state.deck[card_index]
        reversed_state = random.choices([False, True], weights=[2, 1])[0]
        cards.append(
            make_card_snapshot(
                card=card,
                reversed_state=reversed_state,
                position_label=label,
                card_number=card_index + 1,
            )
        )

    inputs = st.session_state.guided_inputs
    themes = [card["theme"] for card in cards]
    theme_counts = {theme: themes.count(theme) for theme in set(themes)}
    dominant_theme = max(theme_counts, key=theme_counts.get)

    action_plan = [
        f"Act on your {cards[1]['title']} message by scheduling one concrete move in the next 48 hours.",
        f"Use the lesson from {cards[0]['title']} to avoid repeating an old pattern this week.",
        f"Prepare for {cards[2]['title']} by writing down one visible outcome tied to your goal: {inputs['goal']}.",
    ]

    narrative = (
        f"Your session starts with {cards[0]['title']}, which points to the recent pattern shaping your work mindset. "
        f"{cards[1]['title']} is the center of gravity right now, suggesting the most useful response is to stay focused on what moves your goal forward. "
        f"{cards[2]['title']} suggests where momentum can build next if you act with consistency instead of urgency."
    )

    reflection = (
        f"You rated your energy at {inputs['energy']}/5 and named this challenge: '{inputs['challenge'] or 'No challenge entered'}'. "
        f"The spread leans most strongly toward {dominant_theme}, so the strongest session takeaway is to align your next action with that theme."
    )

    return {
        "cards": cards,
        "dominant_theme": dominant_theme,
        "narrative": narrative,
        "reflection": reflection,
        "action_plan": action_plan,
    }


def render_progress_header():
    current_step = st.session_state.journey_step
    progress = (current_step + 1) / len(JOURNEY_STEPS)
    st.caption("Guided Career Session")
    st.progress(progress)
    st.write(" -> ".join(JOURNEY_STEPS))


def render_card(card):
    suffix = " (Reversed)" if card["is_reversed"] else ""
    with st.container(border=True):
        st.markdown(
            f"<p style='text-align:center; font-size:64px; margin-bottom:0.1em;'>{card['emoji']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h3 style='text-align:center; margin-bottom:0.2em;'>#{card['card_number']}: {card['title']}{suffix}</h3>",
            unsafe_allow_html=True,
        )
        st.caption(card["position_label"])
        st.info(card["active_meaning"])


def render_deck_browser():
    st.header("Check Deck of Cards", anchor=False, divider="rainbow")
    st.markdown(
        """
        <div style='margin-top: 0.5em; margin-bottom: 0.5em; font-weight: bold; font-size: 1.1em;'>
            Browse all cards and their meanings below. Use the arrows to scroll.
        </div>
        """,
        unsafe_allow_html=True,
    )
    card = INITIAL_DECK[st.session_state.current_card_index]
    st.markdown(
        f"""
        <div class='tarot-card' style='margin: 0 auto; max-width: 340px; background: linear-gradient(135deg, #fff 70%, #f0f0ff 100%); border-radius: 18px; box-shadow: 0 2px 12px 0 rgba(80,80,120,0.10); min-height: 320px; border: 2px solid #e0e0f0; padding: 0.5em 0.5em 0.7em 0.5em;'>
            <div class='tarot-emoji' style='font-size: 3.5em; text-align: center; margin-top: 1.1em; margin-bottom: 0.2em;'>{card['emoji']}</div>
            <div class='tarot-title' style='font-size: 1.25em; font-weight: 600; text-align: center; margin-bottom: 0.2em;'>{card['title']}</div>
            <div class='tarot-meaning' style='font-size: 0.98em; color: #444; text-align: center; margin: 0.5em 0.7em 0.7em 0.7em;'>{card['meaning']}</div>
            <div class='tarot-reversed' style='font-size: 0.92em; color: #888; text-align: center; margin: 0.2em 0.7em 0.7em 0.7em;'><b>Reversed:</b> {card['reversed_meaning']}</div>
            <div style='text-align:center; margin-top:0.5em; color:#888;'>Card {st.session_state.current_card_index + 1} of {len(INITIAL_DECK)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, _, col3 = st.columns([1, 2, 1])
    with col1:
        if (
            st.button("⬅️", key="prev_card", use_container_width=True)
            and st.session_state.current_card_index > 0
        ):
            st.session_state.current_card_index -= 1
    with col3:
        if (
            st.button("➡️", key="next_card", use_container_width=True)
            and st.session_state.current_card_index < len(INITIAL_DECK) - 1
        ):
            st.session_state.current_card_index += 1


def render_check_in():
    st.header("Step 1: Check-in", anchor=False, divider="rainbow")
    inputs = st.session_state.guided_inputs
    inputs["name"] = st.text_input(
        "Name for the session (optional)",
        value=inputs["name"],
    )
    inputs["energy"] = st.slider(
        "How is your energy today?",
        min_value=1,
        max_value=5,
        value=inputs["energy"],
    )
    inputs["goal"] = st.selectbox(
        "What do you want help with most?",
        [
            "Build momentum on an important project",
            "Improve communication at work",
            "Get unstuck and regain focus",
            "Think through a career change",
            "Recover from burnout and reset",
        ],
        index=[
            "Build momentum on an important project",
            "Improve communication at work",
            "Get unstuck and regain focus",
            "Think through a career change",
            "Recover from burnout and reset",
        ].index(inputs["goal"]),
    )
    inputs["challenge"] = st.text_area(
        "What feels most challenging right now?",
        value=inputs["challenge"],
        height=120,
        placeholder="Example: I have too many half-finished tasks and I keep reacting instead of prioritizing.",
    )
    if st.button("Continue to Card Draw", type="primary", use_container_width=True):
        st.session_state.journey_step = 1
        st.rerun()


def render_draw_step():
    st.header("Step 2: Draw Your Starting Card", anchor=False, divider="rainbow")
    st.write(
        "Choose one card to start your session. The next two cards build the full story."
    )
    card_back_design = "🎴"
    cols_top = st.columns(5)
    cols_bottom = st.columns(5)
    for i, col in enumerate(cols_top):
        with col:
            if st.button(
                f"{card_back_design}\n{i + 1}",
                key=f"guided_card_{i}",
                use_container_width=True,
            ):
                st.session_state.selected_seed_index = i
    for i, col in enumerate(cols_bottom):
        with col:
            if st.button(
                f"{card_back_design}\n{i + 6}",
                key=f"guided_card_{i + 5}",
                use_container_width=True,
            ):
                st.session_state.selected_seed_index = i + 5

    if st.session_state.selected_seed_index is not None:
        st.success(
            f"Starting card locked in at position #{st.session_state.selected_seed_index + 1}."
        )
        if st.button("Reveal the Session", type="primary", use_container_width=True):
            time.sleep(0.8)
            st.session_state.guided_reading = build_guided_reading(
                st.session_state.selected_seed_index
            )
            st.session_state.journey_step = 2
            st.rerun()


def render_interpret_step():
    reading = st.session_state.guided_reading
    st.header("Step 3: Interpretation", anchor=False, divider="rainbow")
    cols = st.columns(3)
    for col, card in zip(cols, reading["cards"]):
        with col:
            render_card(card)

    st.subheader("What the spread is saying", anchor=False)
    st.write(reading["narrative"])
    st.write(reading["reflection"])

    if openai.api_key:
        if st.button("Generate AI session recap", use_container_width=True):
            ai_prompt = (
                "You are a thoughtful career reflection coach. "
                "Write a grounded 3-4 sentence recap for this guided tarot session.\n\n"
                f"Goal: {st.session_state.guided_inputs['goal']}\n"
                f"Challenge: {st.session_state.guided_inputs['challenge']}\n"
                f"Energy: {st.session_state.guided_inputs['energy']}/5\n"
                f"Cards: {', '.join([card['title'] + (' reversed' if card['is_reversed'] else '') for card in reading['cards']])}\n"
                f"Narrative: {reading['narrative']}\n"
            )
            with st.spinner("Generating recap..."):
                try:
                    response = openai.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": ai_prompt},
                        ],
                        max_tokens=220,
                        temperature=0.7,
                    )
                    st.success("AI recap")
                    st.write(response.choices[0].message.content.strip())
                except Exception as exc:
                    st.error(f"AI recap failed: {exc}")

    if st.button("Build My Action Plan", type="primary", use_container_width=True):
        st.session_state.journey_step = 3
        st.rerun()


def render_action_plan_step():
    reading = st.session_state.guided_reading
    st.header("Step 4: Action Plan", anchor=False, divider="rainbow")
    st.write(
        "Turn the reading into something useful. Pick one action you will actually do."
    )
    for action in reading["action_plan"]:
        st.markdown(f"- {action}")

    st.text_area(
        "Write your own next move",
        key="user_next_move",
        height=120,
        placeholder="Example: Block 45 minutes tomorrow morning to finish the project outline and send it for feedback.",
    )
    st.text_area(
        "Optional note to future you",
        key="future_note",
        height=100,
        placeholder="What do you want to remember from this session next week?",
    )

    if st.button("Finish Session", type="primary", use_container_width=True):
        st.session_state.journey_step = 4
        st.rerun()


def render_wrap_up():
    reading = st.session_state.guided_reading
    inputs = st.session_state.guided_inputs
    save_current_session()
    st.header("Step 5: Wrap-up", anchor=False, divider="rainbow")
    st.success(
        f"Dominant theme: {reading['dominant_theme'].title()}. Keep your next move small, visible, and tied to your goal."
    )
    session_name = inputs["name"].strip() or "Your"
    share_text = (
        f"{session_name} guided tarot session\n"
        f"Goal: {inputs['goal']}\n"
        f"Challenge: {inputs['challenge'] or 'Not provided'}\n"
        f"Cards: {', '.join([card['title'] + (' reversed' if card['is_reversed'] else '') for card in reading['cards']])}\n"
        f"Takeaway: {reading['narrative']}\n"
        f"Next move: {st.session_state.get('user_next_move', '').strip() or reading['action_plan'][0]}"
    )
    st.text_area("Session summary", value=share_text, height=220)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start a New Session", use_container_width=True):
            reset_journey(reset_deck=True)
            st.rerun()
    with col2:
        if st.button("Reflect on the Cards Again", use_container_width=True):
            st.session_state.journey_step = 2
            st.rerun()


initialize_app_state()

st.title("✨ :rainbow[Pasona Connect] Tarot App Demo")
st.markdown(
    "A playful career reflection app with a longer guided flow. Check in, draw a spread, "
    "interpret the message, and leave with a next step."
)
st.divider()

with st.sidebar:
    st.header("✨ Controls")
    experience_mode = st.radio(
        "Choose a mode:",
        ("Guided Career Session", "Check Deck of Cards"),
        captions=(
            "A longer reflective experience with five steps.",
            "Browse the full deck and meanings.",
        ),
    )

    if st.button("Reset Session", use_container_width=True):
        reset_journey(reset_deck=False)
        st.rerun()

    if st.button("Shuffle Deck", use_container_width=True):
        reset_journey(reset_deck=True)
        st.success("The deck has been shuffled.")
        time.sleep(0.6)
        st.rerun()

    if st.button("Toggle Light/Dark Mode", use_container_width=True):
        toggle_theme()
        st.info(
            f"Theme toggled to {st.session_state.theme_mode.title()}. Streamlit theme changes still depend on Streamlit settings."
        )

if experience_mode == "Check Deck of Cards":
    render_deck_browser()
else:
    render_progress_header()
    render_progress_dashboard()
    step = st.session_state.journey_step
    if step == 0:
        render_check_in()
    elif step == 1:
        render_draw_step()
    elif step == 2:
        render_interpret_step()
    elif step == 3:
        render_action_plan_step()
    else:
        render_wrap_up()

st.markdown(
    """
    <style>
    .tarot-card {
        transition: box-shadow 0.3s, border-color 0.3s, transform 0.25s cubic-bezier(.25,.8,.25,1);
    }
    .tarot-card:hover {
        box-shadow: 0 0 16px 4px #a084ff, 0 2px 12px 0 rgba(80,80,120,0.10);
        border: 2.5px solid #a084ff !important;
        transform: scale(1.06) perspective(600px) rotateY(-2deg) rotateX(2deg);
        z-index: 2;
    }
    .tarot-emoji {
        animation: tarot-bounce 1.2s cubic-bezier(.28,.84,.42,1) infinite alternate;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        text-align: center;
    }
    @keyframes tarot-bounce {
        0%   { transform: translateY(0); }
        40%  { transform: translateY(-18px) scale(1.08); }
        60%  { transform: translateY(-12px) scale(1.04); }
        100% { transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
