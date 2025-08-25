
# 🎭 PlaidLibs™ — The Absurd AI Mad Libs Generator 🧶

PlaidLibs™ is a quirky, AI-powered **Mad Libs-style word game** with a tartan twist.  
Built with **Streamlit**, **Zephyr-7B**, and **FLUX**, it generates absurd, interactive stories by asking you to fill in the blanks with random words and also gernated image from story.  




## ✨ Features
- 🔤 Fill-in-the-blank style prompts (adjectives, nouns, verbs, etc.)
- 🤖 AI-generated absurd & funny storylines aloso image from story
- 🎨 Randomized Scottish tartan (plaid) theme for extra fun
- ⚡ Simple web app built with Streamlit
- 🔄 Interactive “rerun” button to create endless silly stories

---

## 🚀 Quick Start

### 1. Clone this repository
```bash
git clone https://github.com/your-username/plaidlibs.git
cd plaidlibs
````

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your `secrets.toml`

Create a `.streamlit/secrets.toml` file and add your keys (if required, e.g. OpenAI/HF API keys):

```toml
[api_keys]
huggingface = "your_huggingface_token"
```

### 5. Run the app

```bash
streamlit run app.py

## 📂 Project Structure


plaidlibs/
│
├── app.py                 # Main Streamlit app
├── prompts/               # Prompt templates
├── utils/                 # Helper functions
├── requirements.txt       # Python dependencies
└── README.md              # This file


## 🎮 Example Output

> "Once upon a time, a **beautiful** llama decided to **dance** across the **mountain**,
> only to be interrupted by a **mysterious** bagpipe-playing wizard."





## 🧶 Credits

* Streamlit for the UI
* Zephyr-7B + FLUX for the story generation magic
* Inspired by the classic **Mad Libs®** word game



Kya tum chahogi main **requirements.txt** bhi bana dun (Streamlit + HuggingFace + dependencies ke sath), taake upload karte hi log run kar saken?
```
