import os
import json
import datetime
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

def generate_ssid():
    now = datetime.datetime.now()
    return now.strftime("sess_%Y%m%d_%H%M%S")

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

def delete_session(name):
    if not name:
        print(f"{COLOR_RED}Please specify a session ID to delete. E.g. aiuru session --delete sess_20260719_165242{COLOR_RESET}")
        return False
    path = get_session_path(name)
    if not os.path.exists(path):
        print(f"{COLOR_RED}Session '{name}' not found.{COLOR_RESET}")
        return False
    try:
        os.remove(path)
        print(f"{COLOR_GREEN}Session '{name}' deleted successfully.{COLOR_RESET}")
        return True
    except Exception as e:
        print(f"{COLOR_RED}Failed to delete session '{name}': {e}{COLOR_RESET}")
        return False

def get_latest_session():
    if not os.path.exists(SESSIONS_DIR):
        return None
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    if not files:
        return None
    files_with_time = [(f, os.path.getmtime(os.path.join(SESSIONS_DIR, f))) for f in files]
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    return files_with_time[0][0][:-5]

def list_sessions():
    if not os.path.exists(SESSIONS_DIR):
        print(f"{COLOR_YELLOW}No saved sessions found.{COLOR_RESET}")
        return
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
    if not files:
        print(f"{COLOR_YELLOW}No saved sessions found.{COLOR_RESET}")
        return

    files_with_time = []
    for f in files:
        path = os.path.join(SESSIONS_DIR, f)
        mtime = os.path.getmtime(path)
        files_with_time.append((f, mtime, path))

    files_with_time.sort(key=lambda x: x[1], reverse=True)

    headers = ["#", "Session ID (SSID)", "Messages", "Last Updated"]
    rows = []
    for idx, (f, mtime, path) in enumerate(files_with_time, 1):
        ssid = f[:-5]
        mtime_str = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        msg_count = 0
        try:
            with open(path, "r", encoding="utf-8") as sf:
                history = json.load(sf)
                if isinstance(history, list):
                    msg_count = len(history)
        except Exception:
            pass
        rows.append([idx, f"{COLOR_CYAN}{ssid}{COLOR_RESET}", f"{msg_count} msgs", f"{COLOR_DIM}{mtime_str}{COLOR_RESET}"])

    draw_table("SAVED CHAT SESSIONS", headers, rows)

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
