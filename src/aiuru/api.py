import json
import sys
import urllib.request
import urllib.error
from .ui import (
    COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN, COLOR_BOLD, COLOR_RESET, COLOR_DIM, COLOR_WHITE,
    Spinner, draw_table
)
from .config import BASE_URL, save_config

COLOR_BLUE = "\033[34m"

def fetch_models_api(api_key):
    url = f"{BASE_URL}/chat/models-list"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"}, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        url_get = f"{BASE_URL}/models"
        req_get = urllib.request.Request(url_get, headers={"Authorization": f"Bearer {api_key}"}, method="GET")
        try:
            with urllib.request.urlopen(req_get) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                raw_models = res_data.get("data", [])
                return [{"id": m.get("id"), "name": m.get("owned_by", m.get("id"))} for m in raw_models]
        except Exception:
            return None

def change_model_interactive(config):
    api_key = config.get("api_key")
    if not api_key:
        print(f"{COLOR_RED}Please configure API key first using setup{COLOR_RESET}")
        return
    
    print(f"{COLOR_BLUE}Fetching available models...{COLOR_RESET}")
    models = fetch_models_api(api_key)
    if not models:
        print(f"{COLOR_RED}Failed to retrieve models.{COLOR_RESET}")
        return
    
    headers = ["#", "Model ID / Name", "Status"]
    rows = []
    for idx, model in enumerate(models, 1):
        is_current = f"{COLOR_YELLOW}Active (Current){COLOR_RESET}" if str(model["id"]) == str(config.get("default_model")) or model["name"] == config.get("default_model") else "Available"
        rows.append([idx, f"{model['name']} [ID: {model['id']}]", is_current])
        
    draw_table("AVAILABLE MODELS", headers, rows)
        
    try:
        choice = input(f"\n{COLOR_YELLOW}Select model number to set as default: {COLOR_RESET}").strip()
        if not choice:
            return
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(models):
            selected = models[choice_idx]
            config["default_model"] = selected["id"]
            config["default_model_name"] = selected["name"]
            save_config(config)
            print(f"{COLOR_GREEN}Model changed to: {selected['name']} [ID: {selected['id']}]{COLOR_RESET}")
        else:
            print(f"{COLOR_RED}Invalid choice.{COLOR_RESET}")
    except ValueError:
        print(f"{COLOR_RED}Please enter a valid number.{COLOR_RESET}")

def make_completion(config, messages, quiet=False):
    api_key = config.get("api_key")
    model = config.get("default_model", 1)
    
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        model_val = int(model)
    except ValueError:
        model_val = model
        
    payload = {
        "model": model_val,
        "messages": messages,
        "stream": True
    }
    
    spinner = Spinner("AI is writing..." if quiet else "Thinking...")
    spinner.start()
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    
    quota_info = None
    usage_info = None
    response_text = ""
    
    try:
        with urllib.request.urlopen(req) as response:
            spinner.stop()
            
            if not quiet and sys.stdout.isatty():
                print(f"{COLOR_CYAN}{COLOR_BOLD}AI: {COLOR_RESET}", end="", flush=True)
            
            for line in response:
                line_str = line.decode("utf-8").strip()
                if line_str.startswith("data:"):
                    data_content = line_str[5:].strip()
                    if data_content == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_content)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {}).get("content", "")
                            if delta:
                                if not quiet and sys.stdout.isatty():
                                    print(delta, end="", flush=True)
                                response_text += delta
                        
                        if "usage" in chunk:
                            usage_info = chunk["usage"]
                        if "model_quota" in chunk:
                            quota_info = chunk["model_quota"]
                    except Exception:
                        pass
            
            if not quiet and sys.stdout.isatty():
                print()
            
            if quota_info:
                config["last_quota"] = quota_info
                save_config(config)
            
            meta_parts = []
            if usage_info:
                used = usage_info.get("total_tokens", 0)
                prompt_t = usage_info.get("prompt_tokens", 0)
                comp_t = usage_info.get("completion_tokens", 0)
                meta_parts.append(f"Used: {COLOR_GREEN}{used}{COLOR_DIM} t ({prompt_t} prompt, {comp_t} completion)")
            
            if quota_info:
                rem = quota_info.get("daily_remaining_tokens", 0)
                limit = quota_info.get("daily_quota_tokens", 1)
                meta_parts.append(f"Remaining Quota: {COLOR_GREEN}{rem:,}{COLOR_DIM} / {limit:,} t")
                
            if meta_parts and sys.stderr.isatty():
                sys.stderr.write(f"{COLOR_DIM}[ {f' | '.join(meta_parts)} ]{COLOR_RESET}\n")
                sys.stderr.flush()
                
            return response_text
            
    except urllib.error.HTTPError as e:
        spinner.stop()
        print()
        try:
            err_data = json.loads(e.read().decode("utf-8"))
            err_msg = err_data.get("error", {}).get("message", err_data.get("message", str(err_data)))
            print(f"{COLOR_RED}API Error ({e.code}): {err_msg}{COLOR_RESET}")
        except Exception:
            print(f"{COLOR_RED}API Error ({e.code}): {e.reason}{COLOR_RESET}")
    except Exception as e:
        spinner.stop()
        print(f"\n{COLOR_RED}Error: {e}{COLOR_RESET}")
    return None
