import streamlit as st
import random
import time
import copy

# --- App Configuration ---
st.set_page_config(
    page_title="Pasona Tarot for Work",
    page_icon="🔮",
    layout="centered",
)

# --- Card Data ---
# A clean, easily customizable data structure for the 10 cards.
INITIAL_DECK = [
    {
        "title": "The Innovator",
        "emoji": "💡",
        "meaning": "A brilliant new idea will energize your work. Trust your sudden insights.",
    },
    {
        "title": "The Collaborator",
        "emoji": "🤝",
        "meaning": "Your greatest success this week will come from teamwork. Reach out and connect.",
    },
    {
        "title": "The Focus Master",
        "emoji": "🎯",
        "meaning": "Eliminate distractions. Deep, focused work on a single task will yield great results.",
    },
    {
        "title": "The Communicator",
        "emoji": "📣",
        "meaning": "Speak up. Your voice needs to be heard in an important meeting or discussion.",
    },
    {
        "title": "The Restful Achiever",
        "emoji": "🧘",
        "meaning": "Don't confuse activity with progress. Take a break; your best work will follow.",
    },
    {
        "title": "The Bold Leader",
        "emoji": "🦁",
        "meaning": "An opportunity to lead or take ownership of a project will present itself. Seize it.",
    },
    {
        "title": "The Student",
        "emoji": "📚",
        "meaning": "A skill you need to learn is holding you back. Dedicate time to learning it.",
    },
    {
        "title": "The Finisher",
        "emoji": "🏁",
        "meaning": "Stop starting and start finishing. Push that lingering project across the finish line.",
    },
    {
        "title": "The Networker",
        "emoji": "🌐",
        "meaning": "The solution to your problem lies with someone you haven't met yet. Expand your network.",
    },
    {
        "title": "The Organizer",
        "emoji": "🧹",
        "meaning": "Clarity comes from order. Tidy your workspace, organize your files, and plan your week.",
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
        st.markdown(
            f"<p style='text-align: center; font-style: italic; font-size: 18px;'>{card['meaning']}</p>",
            unsafe_allow_html=True,
        )

# --- Main App ---

# Initialize the deck on the first run
initialize_deck()

# --- Title and Introduction ---
st.title("🔮 Pasona Tarot for Work")
st.markdown(
    "Get a little dose of fun, lighthearted career advice. "
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
        st.success("The deck has been shuffled!")
        time.sleep(1) # a little pause to let the user see the message
        st.rerun()

    st.markdown("---")
    reading_type = st.radio(
        "Choose your reading:",
        ("Single Card Draw", "3-Card Career Reading"),
        captions=("Quick daily insight.", "Past, Present, and Future outlook.")
    )

# --- Main Interaction Area ---
st.subheader("Pick Your Number", anchor=False)
selected_number = st.number_input(
    "Enter a number between 1 and 10:",
    min_value=1,
    max_value=10,
    value=None, # no default value
    placeholder="Type your number...",
    label_visibility="collapsed"
)

# --- Card Drawing Logic ---
if st.button("Draw Your Card(s)!", type="primary", use_container_width=True, disabled=(selected_number is None)):
    
    # Using the selected number to create a deterministic "seed" index
    # Subtract 1 for zero-based list indexing
    seed_index = selected_number - 1

    # Bonus: Use a spinner for a little dramatic flair
    with st.spinner("Drawing from the deck..."):
        time.sleep(1.5) # Simulate the drawing process

    # --- Single Card Reading ---
    if reading_type == "Single Card Draw":
        # The same number will always draw the same card from the *current* shuffle
        drawn_card = st.session_state.deck[seed_index]
        display_card(drawn_card)

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

        # Bonus: Use st.columns for a clean side-by-side layout
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("<h4 style='text-align: center;'>Past Influence</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card1['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card1['title']}</h5>", unsafe_allow_html=True)
            st.write(card1['meaning'])

        with col2:
            st.markdown("<h4 style='text-align: center;'>Present Focus</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card2['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card2['title']}</h5>", unsafe_allow_html=True)
            st.write(card2['meaning'])

        with col3:
            st.markdown("<h4 style='text-align: center;'>Future Potential</h4>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 60px;'>{card3['emoji']}</p>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: center;'>{card3['title']}</h5>", unsafe_allow_html=True)
            st.write(card3['meaning'])