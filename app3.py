# plaidlibs_app.py
import os
import io
import random
from datetime import datetime
from typing import Optional, Tuple

import streamlit as st
from PIL import Image

# LangChain (chat text model)
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import SystemMessage, HumanMessage

# HF image client
from huggingface_hub import InferenceClient

# ------------------------------
# Page config & token handling
# ------------------------------
st.set_page_config(page_title="🎭 PlaidLibs™", layout="centered")

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "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")  # apna HF token daalna

# ------------------------------
# Models (cached)
# ------------------------------
@st.cache_resource
def load_chat_model() -> ChatHuggingFace:
    llm = HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="conversational",
        max_new_tokens=500,
        temperature=0.9,
        huggingfacehub_api_token=HF_TOKEN,
    )
    return ChatHuggingFace(llm=llm)

@st.cache_resource
def init_image_client() -> InferenceClient:
    return InferenceClient(token=HF_TOKEN)

chat_model = load_chat_model()
image_client = init_image_client()

# ------------------------------
# Narrators, formats, slots
# ------------------------------
NARRATORS = {
    "macquip": ("MacQuip™", "sarcastic Highland bard"),
    "donquip": ("DonQuip™", "mob boss of punchlines"),
    "soquip":  ("SoQuip™", "soulful Southern philosopher"),
    "quip":    ("Quip™", "neutral narrator fallback"),
    "random":  ("Remix Randomizer", "let fate decide"),
}
NARRATOR_LIST = [
    ("1", "MacQuip™", "sarcastic Highland bard"),
    ("2", "DonQuip™", "mob boss of punchlines"),
    ("3", "Quip™",    "neutral narrator fallback"),
    ("4", "SoQuip™",  "soulful Southern philosopher"),
    ("5", "Remix Randomizer", "let fate decide"),
]

FORMATS = ["Short Story", "Ballad", "Breaking News", "Absurd How-To", "Fable", "Wild Card"]
GENRES  = ["Fantasy", "Sci-Fi", "Mystery", "Horror", "Comedy", "Wild Card"]
ABSURDS = ["Mild Plaid", "Medium Plaid", "Full Tartan", "Plaidemonium™"]

WORD_SLOTS = [
    ("adjective",      "First off—hand me an *adjective*. Something juicy."),
    ("silly_object",   "Now give me a *silly object*."),
    ("famous_person",  "Next—name a *famous person*."),
    ("animal",         "Now an *animal*."),
    ("verb_ing",       "A *verb ending in -ing*."),
    ("food",           "Now—*food*."),
    ("place",          "Give me a *place*."),
    ("strange_sound",  "Lastly—hit me with a *strange sound*."),
]

# ------------------------------
# Session state initialization
# ------------------------------
def init_state():
    st.session_state.setdefault("phase", "narrator")
    st.session_state.setdefault("narrator_name", None)
    st.session_state.setdefault("narrator_desc", None)
    st.session_state.setdefault("story_format", None)
    st.session_state.setdefault("genre", None)
    st.session_state.setdefault("absurdity", None)
    st.session_state.setdefault("words", {})
    st.session_state.setdefault("word_index", 0)
    st.session_state.setdefault("story", None)
    st.session_state.setdefault("img", None)
    st.session_state.setdefault("history", [])

def say(role: str, text: str):
    st.session_state.history.append((role, text))

def narrator_prefix():
    return st.session_state.narrator_name or "Narrator"

init_state()

# ------------------------------
# Boot message
# ------------------------------
if not st.session_state.history:
    menu = "\n".join([f"{n}. {name} – {desc}" for (n, name, desc) in NARRATOR_LIST])
    say("assistant",
        "Welcome to **PlaidLibs™** — choose your Quip narrator.\n"
        "Type **number** or **name** (or `random`):\n\n" + menu
    )

# ------------------------------
# UI: chat transcript rendering
# ------------------------------
st.title("🎭 PlaidLibs™")
for role, msg in st.session_state.history:
    with st.chat_message("assistant" if role == "assistant" else "user"):
        st.markdown(msg)

# ------------------------------
# Helpers
# ------------------------------
def pick_from_list(user_text: str, items: list) -> Optional[str]:
    t = user_text.strip().lower()
    if t.isdigit():
        idx = int(t) - 1
        if 0 <= idx < len(items):
            return items[idx]
    for it in items:
        if it.lower() == t:
            return it
    if "random" in t or "wild" in t:
        return random.choice(items)
    return None

def pick_narrator(user_text: str) -> Optional[Tuple[str, str]]:
    t = user_text.strip().lower()
    if t in {"1","2","3","4","5"}:
        key = list(NARRATORS.keys())[int(t)-1]
        return NARRATORS[key]
    for _, name, desc in NARRATOR_LIST:
        if name.lower() == t:
            return (name, desc)
    if "random" in t or "wild" in t:
        n, d = random.choice([(name, desc) for _, name, desc in NARRATOR_LIST])
        return (n, d)
    return None

def recap_words() -> str:
    w = st.session_state.words
    return (
        f"we’ve got a **{w.get('adjective','?')} {w.get('silly_object','?')}**, "
        f"**{w.get('famous_person','?')}** on speed-dial, "
        f"a **{w.get('verb_ing','?')} {w.get('animal','?')}**, "
        f"fuelled by a **{w.get('food','?')}**, "
        f"in a **{w.get('place','?')}** with **{w.get('strange_sound','?')}**."
    )

def story_system_prompt() -> str:
    return (
        "You are a quirky AI narrator that writes PlaidLibs-style absurd stories. "
        "Use the persona, format, genre, and words provided."
    )

def story_human_prompt() -> str:
    nname = st.session_state.narrator_name
    ndesc = st.session_state.narrator_desc
    fmt   = st.session_state.story_format
    gen   = st.session_state.genre
    absd  = st.session_state.absurdity
    w     = st.session_state.words
    return f"""
Narrator: {nname} — {ndesc}
Format: {fmt}
Genre: {gen}
Absurdity: {absd}

Words:
- Adjective: {w.get('adjective','')}
- Silly Object: {w.get('silly_object','')}
- Famous Person: {w.get('famous_person','')}
- Animal: {w.get('animal','')}
- Verb(-ing): {w.get('verb_ing','')}
- Food: {w.get('food','')}
- Place: {w.get('place','')}
- Strange Sound: {w.get('strange_sound','')}

Write an entertaining PlaidLibs-style story.
"""

def generate_story() -> str:
    messages = [
        SystemMessage(content=story_system_prompt()),
        HumanMessage(content=story_human_prompt())
    ]
    res = chat_model.invoke(messages)
    return res.content if hasattr(res, "content") else str(res)

# ------------------------------
# Input handling
# ------------------------------
user_msg = st.chat_input("Type your reply…")
if user_msg:
    say("user", user_msg)
    phase = st.session_state.phase
    low = user_msg.strip().lower()

    # --- EXTRA commands after story ---
    if phase == "story" and low in {"image", "img"}:
        try:
            with st.spinner("🎨 Generating image..."):
                img = image_client.text_to_image(
                    prompt=st.session_state.story[:500],
                    model="black-forest-labs/FLUX.1-dev"
                )
            st.session_state.img = img
            st.image(img, caption="Your PlaidLibs™ Image")
            say("assistant", "Here’s your generated art! Now type **save** to download story + image. 💾")
        except Exception as e:
            say("assistant", f"Image failed: `{e}`")
        st.stop()

    if phase == "story" and low in {"save"}:
        if st.session_state.story and st.session_state.img:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save story text
            story_file = f"PlaidLibs_{ts}.txt"
            with open(story_file, "w", encoding="utf-8") as f:
                f.write(st.session_state.story)

            # Save image
            img_file = f"PlaidLibs_{ts}.png"
            st.session_state.img.save(img_file)

            say("assistant", f"✅ Saved!\n- Story: `{story_file}`\n- Image: `{img_file}`")
            st.download_button("⬇️ Download Story TXT", data=st.session_state.story, file_name=story_file)
            buf = io.BytesIO()
            st.session_state.img.save(buf, format="PNG")
            st.download_button("⬇️ Download Image PNG", data=buf.getvalue(), file_name=img_file, mime="image/png")
        else:
            say("assistant", "You need a story + image before saving.")
        st.stop()

    # --- Normal flow ---
    if phase == "narrator":
        pick = pick_narrator(user_msg)
        if pick:
            name, desc = pick
            st.session_state.narrator_name = name
            st.session_state.narrator_desc = desc
            st.session_state.phase = "format"
            say("assistant",
                f"**{name}** here. Now choose your **literary style**:\n" +
                "\n".join([f"{i+1}. {v}" for i,v in enumerate(FORMATS)]) +
                "\n\nType number/name or `random`.")
        else:
            menu = "\n".join([f"{n}. {name} – {desc}" for (n,name,desc) in NARRATOR_LIST])
            say("assistant", "Please choose:\n" + menu)

    elif phase == "format":
        pick = pick_from_list(user_msg, FORMATS)
        if pick:
            st.session_state.story_format = pick
            st.session_state.phase = "genre"
            say("assistant",
                f"{narrator_prefix()} chuckles: **{pick}** it is!\nNow pick a **genre**:\n" +
                "\n".join([f"{i+1}. {v}" for i,v in enumerate(GENRES)]))
        else:
            say("assistant", "Choose style by number/name.")

    elif phase == "genre":
        pick = pick_from_list(user_msg, GENRES)
        if pick:
            st.session_state.genre = pick
            st.session_state.phase = "absurdity"
            say("assistant",
                f"{narrator_prefix()} smirks: **{pick}** shall guide our tale.\nChoose **absurdity**:\n" +
                "\n".join([f"{i+1}. {v}" for i,v in enumerate(ABSURDS)]))
        else:
            say("assistant", "Choose genre by number/name.")

    elif phase == "absurdity":
        pick = pick_from_list(user_msg, ABSURDS)
        if pick:
            st.session_state.absurdity = pick
            st.session_state.phase = "words"
            st.session_state.word_index = 0
            slot, prompt_line = WORD_SLOTS[0]
            say("assistant", f"Setup locked! {narrator_prefix()} says: {prompt_line}")
        else:
            say("assistant", "Choose absurdity by number/name.")

    elif phase == "words":
        idx = st.session_state.word_index
        slot_key, _ = WORD_SLOTS[idx]
        st.session_state.words[slot_key] = user_msg.strip()
        idx += 1
        if idx < len(WORD_SLOTS):
            st.session_state.word_index = idx
            _, prompt_line = WORD_SLOTS[idx]
            say("assistant", f"{narrator_prefix()} asks: {prompt_line}")
        else:
            st.session_state.phase = "story"
            say("assistant", f"{narrator_prefix()} recaps: {recap_words()}\nNow weaving the tale… 🪄")
            try:
                with st.spinner("Spinning up nonsense…"):
                    story = generate_story()
                    st.session_state.story = story
                say("assistant", f"**📖 Your Story**\n\n{story}\n\nType **image** to create art 🎨")
            except Exception as e:
                say("assistant", f"Story failed: `{e}`")
