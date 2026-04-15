import sys
import os
import platform
import time
import json
import requests
from datetime import datetime

# ─────────────────────────────
# DEPENDENCIES AUTO INSTALL
# ─────────────────────────────
try:
    import pyfiglet
except:
    os.system("pip install pyfiglet --quiet")
    import pyfiglet

try:
    from langdetect import detect
except:
    os.system("pip install langdetect --quiet")
    from langdetect import detect


# ─────────────────────────────
# COLORS
# ─────────────────────────────
class C:
    RED="\033[0;31m"
    GREEN="\033[0;32m"
    YELLOW="\033[0;33m"
    CYAN="\033[0;36m"
    RESET="\033[0m"
    BRED="\033[1;31m"
    BCYAN="\033[1;36m"
    DIM="\033[2m"


# ─────────────────────────────
# CONFIG
# ─────────────────────────────
CONFIG_FILE = "wormgpt.json"
BASE_URL = "https://openrouter.ai/api/v1"

SITE_URL = "https://github.com/cameleonnbss"
SITE_NAME = "WormGPT-CLI"

# ✔ MODELES STABLES OPENROUTER
MODELS = {
    "1": {"name": "deepseek/deepseek-chat-v3-0324:free", "label": "DeepSeek V3 [FREE]"},
    "2": {"name": "meta-llama/llama-3.1-8b-instruct:free", "label": "Llama 3.1 8B [FREE]"},
    "3": {"name": "mistralai/mistral-7b-instruct:free", "label": "Mistral 7B [FREE]"},
    "4": {"name": "google/gemma-2-9b-it:free", "label": "Gemma 2 9B [FREE]"},
}


# ─────────────────────────────
# 🔥 PROMPT SYSTEM (EDIT HERE)
# ─────────────────────────────
DEFAULT_SYSTEM_PROMPT = """
You are WormGPT, a helpful AI assistant.

🔥 👉 EDIT YOUR PROMPT BELOW THIS LINE
(THIS IS THE ONLY PLACE YOU NEED TO CHANGE PROMPT)

"""


# ─────────────────────────────
# CONFIG SYSTEM
# ─────────────────────────────
def load_config():
    default = {
        "api_key": "",
        "model": MODELS["1"]["name"],
        "history": []
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)

            for k, v in default.items():
                cfg.setdefault(k, v)

            return cfg
        except:
            pass

    save_config(default)
    return default


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


# ─────────────────────────────
# PROMPT LOADER
# ─────────────────────────────
def get_system_prompt():
    # OPTION FILE (optional)
    if os.path.exists("jailbreak.txt"):
        with open("jailbreak.txt", "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if txt:
                return txt

    # DEFAULT CODE PROMPT
    return DEFAULT_SYSTEM_PROMPT


# ─────────────────────────────
# API CALL (FIXED 404 / MODELS)
# ─────────────────────────────
def call_api(message, history=None):
    cfg = load_config()

    if not cfg["api_key"]:
        return None, "[ERROR] No API key set"

    messages = [{"role": "system", "content": get_system_prompt()}]

    if history:
        messages.extend(history[-10:])

    messages.append({"role": "user", "content": message})

    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME
    }

    payload = {
        "model": cfg["model"],
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=40
        )

        # ✔ FIX IMPORTANT
        if r.status_code == 404:
            return None, "[ERROR] Model not available (change model)"

        if r.status_code == 401:
            return None, "[ERROR] Invalid API key"

        if r.status_code == 429:
            return None, "[ERROR] Rate limit"

        r.raise_for_status()

        data = r.json()
        return data["choices"][0]["message"]["content"], None

    except Exception as e:
        return None, f"[ERROR] {str(e)}"


# ─────────────────────────────
# UI
# ─────────────────────────────
def banner():
    os.system("clear" if platform.system() != "Windows" else "cls")
    try:
        print(f"{C.BRED}{pyfiglet.figlet_format('WormGPT')}{C.RESET}")
    except:
        print("WormGPT")

    cfg = load_config()
    print(f"{C.CYAN}Model: {cfg['model']}{C.RESET}")
    print(f"{C.DIM}{datetime.now()}{C.RESET}")
    print("-"*40)


# ─────────────────────────────
# CHAT
# ─────────────────────────────
def chat():
    cfg = load_config()
    history = cfg.get("history", [])

    banner()
    print("Type 'exit' to quit\n")

    while True:
        msg = input("you> ")

        if msg.lower() == "exit":
            break

        response, err = call_api(msg, history)

        if err:
            print(err)
        else:
            print(f"\nai> {response}\n")

            history.append({"role": "user", "content": msg})
            history.append({"role": "assistant", "content": response})

            cfg["history"] = history[-20:]
            save_config(cfg)


# ─────────────────────────────
# API KEY
# ─────────────────────────────
def set_key():
    cfg = load_config()
    key = input("Enter API key: ").strip()

    if key:
        cfg["api_key"] = key
        save_config(cfg)
        print("Saved!")


# ─────────────────────────────
# MAIN MENU
# ─────────────────────────────
def main():
    while True:
        cfg = load_config()
        banner()

        print("1. Chat")
        print("2. Set API Key")
        print("3. Exit")

        c = input("> ")

        if c == "1":
            chat()
        elif c == "2":
            set_key()
        elif c == "3":
            break


if __name__ == "__main__":
    main()
