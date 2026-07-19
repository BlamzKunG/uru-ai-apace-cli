import os
import json
from .ui import (
    COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN, COLOR_WHITE, COLOR_DIM, COLOR_BOLD, COLOR_RESET,
    draw_table
)

# Configuration constants
CONFIG_DIR = os.path.expanduser("~/.config/aiuru")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
SESSIONS_DIR = os.path.join(CONFIG_DIR, "sessions")
BASE_URL = "https://gen.ai.kku.ac.th/uruacth/api/v1"

# GitHub Configuration for self-update (Change these before pushing to GitHub)
GITHUB_USER = "BlamzKunG"
GITHUB_REPO = "uru-ai-apace-cli"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"{COLOR_RED}Error saving config: {e}{COLOR_RESET}")

def get_session_path(name):
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return os.path.join(SESSIONS_DIR, f"{name}.json")

def save_session(name, chat_history, quiet=False):
    path = get_session_path(name)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chat_history, f, indent=2, ensure_ascii=False)
        if not quiet:
            print(f"{COLOR_GREEN}Session '{name}' saved successfully.{COLOR_RESET}")
    except Exception as e:
        if not quiet:
            print(f"{COLOR_RED}Failed to save session: {e}{COLOR_RESET}")

def load_session(name):
    path = get_session_path(name)
    if not os.path.exists(path):
        print(f"{COLOR_RED}Session '{name}' not found.{COLOR_RESET}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"{COLOR_RED}Failed to load session: {e}{COLOR_RESET}")
        return None

def list_sessions():
    if not os.path.exists(SESSIONS_DIR):
        print(f"{COLOR_YELLOW}No saved sessions found.{COLOR_RESET}")
        return
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    if not files:
        print(f"{COLOR_YELLOW}No saved sessions found.{COLOR_RESET}")
        return
    print(f"{COLOR_BOLD}{COLOR_CYAN}Saved Sessions:{COLOR_RESET}")
    for idx, f in enumerate(files, 1):
        name = f[:-5]
        print(f"{COLOR_GREEN}{idx}. {COLOR_WHITE}{name}{COLOR_RESET}")

def print_quota_info(config):
    quota = config.get("last_quota")
    if not quota:
        print(f"{COLOR_YELLOW}No quota information available yet. Run a prompt to fetch quota.{COLOR_RESET}")
        return
    
    limit = quota.get("daily_quota_tokens", 0)
    used = quota.get("daily_usage_tokens", 0)
    remaining = quota.get("daily_remaining_tokens", 0)
    
    percent_used = (used / limit * 100) if limit > 0 else 0
    
    headers = ["Metric", "Value"]
    rows = [
        ["Daily Limit", f"{limit:,} tokens"],
        ["Used Tokens", f"{COLOR_RED}{used:,}{COLOR_RESET} tokens ({percent_used:.2f}%)"],
        ["Remaining Tokens", f"{COLOR_GREEN}{remaining:,}{COLOR_RESET} tokens"]
    ]
    
    draw_table("DAILY QUOTA STATUS", headers, rows)
    print(f"{COLOR_DIM}Note: Quota resets daily.{COLOR_RESET}")
