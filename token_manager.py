import os
import json

TOKEN_FILE = "/data/tokens.json"  # ← Zeabur で永続化される場所！

def load_tokens():
    if not os.path.exists(TOKEN_FILE):
        return {"access": None, "refresh": None}
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

def save_tokens(access, refresh):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"access": access, "refresh": refresh}, f)
