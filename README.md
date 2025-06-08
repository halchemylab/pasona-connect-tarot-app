# Pasona Connect Tarot App Demo

🔮 A fun, interactive tarot-inspired app for career and work advice, built with Streamlit.

## Project Description

Pasona Tarot for Work is a web application that lets users draw virtual tarot cards for lighthearted, motivational career guidance. Each card offers unique advice or insight, with both upright and reversed meanings. Users can choose between a single-card daily reading or a 3-card career spread (Past, Present, Future).

## Features

- 10 custom work/career-themed tarot cards, each with emoji, title, and dual meanings
- Shuffle the deck at any time for a fresh reading
- Choose between a single card or a 3-card spread
- Interactive UI with card-flip animation and sharing option
- Built with [Streamlit](https://streamlit.io/) for easy deployment and use

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pasona-connect-tarot-app.git
   cd pasona-connect-tarot-app
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the app locally with Streamlit:

```bash
streamlit run app.py
```

Then open the provided local URL in your browser (usually http://localhost:8501).

## Example

![Screenshot of Pasona Tarot for Work](screenshot.png)

## Project Structure

- `app.py` — Main Streamlit application
- `requirements.txt` — Python dependencies
- `README.md` — Project documentation

## Customization

You can easily edit the `INITIAL_DECK` in `app.py` to add, remove, or modify cards and their meanings.

## License

MIT License. See [LICENSE](LICENSE) for details.