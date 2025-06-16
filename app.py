
import streamlit as st
import random
import time
import copy
import os
from dotenv import load_dotenv
import openai

# --- App Configuration ---
st.set_page_config(
    page_title="Pasona Connect Tarot App Demo",
    page_icon="🔮",
    layout="centered",
)

# --- Load environment variables and set OpenAI API key ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Card Data ---
# A clean, easily customizable data structure for the 10 cards.
INITIAL_DECK = [
    {
        "title": "The Innovator",
        "emoji": "💡",
        "meaning": "A brilliant new idea will energize your work. Trust your sudden insights.",
        "reversed_meaning": "You're experiencing creative block. Step away and seek new inspiration."
    },
    {
        "title": "The Collaborator",
        "emoji": "🤝",
        "meaning": "Your greatest success this week will come from teamwork. Reach out and connect.",
        "reversed_meaning": "Teamwork is faltering. Address miscommunication or try working solo for a bit."
    },
    {
        "title": "The Focus Master",
        "emoji": "🎯",
        "meaning": "Eliminate distractions. Deep, focused work on a single task will yield great results.",
        "reversed_meaning": "Scattered attention is holding you back. Reassess your priorities."
    },
    {
        "title": "The Communicator",
        "emoji": "📣",
        "meaning": "Speak up. Your voice needs to be heard in an important meeting or discussion.",
        "reversed_meaning": "Misunderstandings may arise. Listen carefully and clarify your message."
    },
    {
        "title": "The Restful Achiever",
        "emoji": "🧘",
        "meaning": "Don't confuse activity with progress. Take a break; your best work will follow.",
        "reversed_meaning": "Restlessness or burnout is near. Prioritize self-care and boundaries."
    },
    {
        "title": "The Bold Leader",
        "emoji": "🦁",
        "meaning": "An opportunity to lead or take ownership of a project will present itself. Seize it.",
        "reversed_meaning": "Overconfidence or reluctance to lead may cause setbacks. Reflect before acting."
    },
    {
        "title": "The Student",
        "emoji": "📚",
        "meaning": "A skill you need to learn is holding you back. Dedicate time to learning it.",
        "reversed_meaning": "Avoiding growth or ignoring feedback will stall your progress."
    },
    {
        "title": "The Finisher",
        "emoji": "🏁",
        "meaning": "Stop starting and start finishing. Push that lingering project across the finish line.",
        "reversed_meaning": "Procrastination or perfectionism is blocking completion. Let go and finish."
    },
    {
        "title": "The Networker",
        "emoji": "🌐",
        "meaning": "The solution to your problem lies with someone you haven't met yet. Expand your network.",
        "reversed_meaning": "Networking efforts may feel forced or unproductive. Focus on genuine connections."
    },
    {
        "title": "The Organizer",
        "emoji": "🧹",
        "meaning": "Clarity comes from order. Tidy your workspace, organize your files, and plan your week.",
        "reversed_meaning": "Disorganization is causing confusion. Take time to restore order."
    },
]

# --- State Management ---
# Use st.session_state to initialize and persist the deck across reruns.
def initialize_deck():
    """Initializes or shuffles the deck in the session state."""
    if "deck" not in st.session_state:
        # On first run, create a shuffled version of the deck.
        shuffled_deck = copy.deepcopy(INITIAL_DECK)
        random.shuffle(shuffled_deck)
        st.session_state.deck = shuffled_deck

# --- UI Helper Functions ---
def display_card(card, header="Your Card"):
    """Displays a single card in a formatted, centered layout."""
    with st.container(border=True):
        st.header(header, anchor=False, divider="rainbow")
        st.markdown(
            f"<p style='text-align: center; font-size: 80px;'>{card['emoji']}</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h2 style='text-align: center;'>{card['title']}</h2>",
            unsafe_allow_html=True,
        )

# --- Main App ---

# Initialize the deck on the first run
initialize_deck()

# --- Title and Introduction ---
st.title("✨ :rainbow[Pasona Connect] Tarot App Demo")
st.markdown(
    "Get a little dose of fun, lighthearted career advice. "
    "Designed specifically for Pasona Connect! "
    "Pick a number from 1 to 10 to draw your card for the day."
)
st.divider()

# --- Controls in the Sidebar ---
with st.sidebar:
    st.header("✨ Controls")
    
    # The Shuffle button reruns the shuffling logic for the session_state deck
    if st.button("Shuffle Deck", use_container_width=True):
        shuffled_deck = copy.deepcopy(INITIAL_DECK)
        random.shuffle(shuffled_deck)
        st.session_state.deck = shuffled_deck
        # Reset all relevant session state variables for a true app reset
        st.session_state.chosen_card_index = -1
        st.session_state.show_share = False
        st.session_state.last_share_btn = False
        st.success("The deck has been shuffled and the app has been reset!")
        time.sleep(1) # a little pause to let the user see the message
        st.rerun()

    st.markdown("---")
    reading_type = st.radio(
        "Choose your reading:",
        ("Single Card Draw", "3-Card Career Reading"),
        captions=("Quick daily insight.", "Past, Present, and Future outlook.")
    )

# --- Main Interaction Area ---
st.subheader("Click a Card to Draw Your Reading", anchor=False)

card_backs_cols = st.columns(5)
card_back_design = "🎴"

# Use session_state to persist chosen card index
if "chosen_card_index" not in st.session_state:
    st.session_state.chosen_card_index = -1

# First row (cards 1-5)
for i, col in enumerate(card_backs_cols):
    with col:
        card_number = i + 1
        if st.button(f"{card_back_design}\n{card_number}", key=f"card_{i}", use_container_width=True):
            st.session_state.chosen_card_index = i

# Second row (cards 6-10)
card_backs_cols_2 = st.columns(5)
for i, col in enumerate(card_backs_cols_2):
    with col:
        card_number = i + 6
        if st.button(f"{card_back_design}\n{card_number}", key=f"card_{i+5}", use_container_width=True):
            st.session_state.chosen_card_index = i + 5

# --- Card Drawing Logic ---
if st.session_state.chosen_card_index != -1:
    with st.spinner("Drawing from the deck..."):
        time.sleep(1.0)

    seed_index = st.session_state.chosen_card_index

    # --- Single Card Reading ---
    if reading_type == "Single Card Draw":
        placeholder = st.empty()  # Create an empty container for the animation

        # 1. Show the card back
        with placeholder.container(border=True):
            st.markdown("<p style='text-align: center; font-size: 150px; line-height: 1.2;'>🎴</p>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center;'>Your Card</h3>", unsafe_allow_html=True)

        time.sleep(3)  # Pause on the card back for 4 full seconds
        st.balloons()

        # 2. "Flip" the card by replacing the placeholder's content
        drawn_card = st.session_state.deck[seed_index]
        is_reversed = random.choice([True, False])  # Restore 50/50 chance
        card_number = seed_index + 1
        with placeholder.container(border=True):
            if is_reversed:
                st.header(f"Your Card (Reversed) — #{card_number}", anchor=False, divider="rainbow")
                st.markdown(f"<p style='text-align: center; font-size: 80px;'>{drawn_card['emoji']}</p>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center;'>#{card_number}: {drawn_card['title']}</h2>", unsafe_allow_html=True)
                st.info(f"**Reversed Meaning:** {drawn_card['reversed_meaning']}")
            else:
                st.header(f"Your Card — #{card_number}", anchor=False, divider="rainbow")
                st.markdown(f"<p style='text-align: center; font-size: 80px;'>{drawn_card['emoji']}</p>", unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align: center;'>#{card_number}: {drawn_card['title']}</h2>", unsafe_allow_html=True)
                st.info(f"**Meaning:** {drawn_card['meaning']}")

        # --- Share to Teams Button ---
        st.divider()
        reading_text = f"""🔮 My Pasona Tarot Reading:\n**{drawn_card['title']}** {drawn_card['emoji']}\n*_{drawn_card['reversed_meaning'] if is_reversed else drawn_card['meaning']}_*\n"""
        # Make the share section hidable with persistent state
        if "show_share" not in st.session_state:
            st.session_state.show_share = False
        if "last_share_btn" not in st.session_state:
            st.session_state.last_share_btn = False
        share_btn = st.button(
            "Show shareable reading text" if not st.session_state.show_share else "Hide shareable reading text",
            key="toggle_share_btn"
        )
        if share_btn and not st.session_state.last_share_btn:
            st.session_state.show_share = not st.session_state.show_share
        st.session_state.last_share_btn = share_btn
        if st.session_state.show_share:
            st.text_area("Copy this to share your reading!", reading_text, height=150)

    # --- 3-Card Reading ---
    elif reading_type == "3-Card Career Reading":
        st.header("Your Career Reading", anchor=False, divider="rainbow")
        # Draw 3 cards sequentially from the seeded position, wrapping around if needed
        card1_index = seed_index
        card2_index = (seed_index + 1) % 10 # Modulo for wrapping around the deck
        card3_index = (seed_index + 2) % 10

        card1 = st.session_state.deck[card1_index]
        card2 = st.session_state.deck[card2_index]
        card3 = st.session_state.deck[card3_index]

        # Decide reversed state for each card
        reversed1 = random.choice([True, False])
        reversed2 = random.choice([True, False])
        reversed3 = random.choice([True, False])

        # Bonus: Use st.columns for a clean side-by-side layout
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<h4 style='text-align: center;'>Past Influence</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card1['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card1['title']}{' (Reversed)' if reversed1 else ''}</h5>", unsafe_allow_html=True)
            if reversed1:
                st.info(f"**Reversed Meaning:** {card1['reversed_meaning']}")
            else:
                st.info(f"**Meaning:** {card1['meaning']}")

        with col2:
            st.markdown("<h4 style='text-align: center;'>Present Focus</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card2['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card2['title']}{' (Reversed)' if reversed2 else ''}</h5>", unsafe_allow_html=True)
            if reversed2:
                st.info(f"**Reversed Meaning:** {card2['reversed_meaning']}")
            else:
                st.info(f"**Meaning:** {card2['meaning']}")

        with col3:
            st.markdown("<h4 style='text-align: center;'>Future Potential</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card3['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card3['title']}{' (Reversed)' if reversed3 else ''}</h5>", unsafe_allow_html=True)
            if reversed3:
                st.info(f"**Reversed Meaning:** {card3['reversed_meaning']}")
            else:
                st.info(f"**Meaning:** {card3['meaning']}")

        # --- AI Explanation Section ---
        if openai.api_key:
            ai_prompt = (
                f"""
                You are a career coach tarot expert. Given the following 3-card tarot reading, provide a concise, insightful summary (2-4 sentences) that connects the cards' meanings to a career context. Use a friendly, encouraging tone.

                Past Influence: {card1['title']} ({'Reversed' if reversed1 else 'Upright'}) - {card1['reversed_meaning'] if reversed1 else card1['meaning']}
                Present Focus: {card2['title']} ({'Reversed' if reversed2 else 'Upright'}) - {card2['reversed_meaning'] if reversed2 else card2['meaning']}
                Future Potential: {card3['title']} ({'Reversed' if reversed3 else 'Upright'}) - {card3['reversed_meaning'] if reversed3 else card3['meaning']}
                """
            )
            if st.button("Get AI Career Explanation", key="ai_explain_btn"):
                with st.spinner("Asking the AI for your career insight..."):
                    try:
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": ai_prompt}
                            ],
                            max_tokens=200,
                            temperature=0.7,
                        )
                        ai_text = response.choices[0].message.content.strip()
                        st.success("AI Career Explanation:")
                        st.write(ai_text)
                    except Exception as e:
                        st.error(f"AI explanation failed: {e}")
        else:
            st.info("Add your OpenAI API key to the .env file to enable AI explanations.")