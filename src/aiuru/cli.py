import os
import sys
import argparse
import urllib.request
import json
import subprocess

from . import __version__

from .ui import (
    COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN, COLOR_BOLD, COLOR_RESET, COLOR_DIM, COLOR_PURPLE, COLOR_BLUE, COLOR_WHITE,
    print_banner, draw_table
)
from .config import (
    load_config, save_config, get_session_path, save_session, load_session, list_sessions, print_quota_info,
    GITHUB_USER, GITHUB_REPO
)
from .api import (
    fetch_models_api, change_model_interactive, make_completion
)
from .editor import (
    handle_file_edit
)

def run_self_update():
    if GITHUB_USER == "YOUR_GITHUB_USERNAME":
        print(f"{COLOR_RED}Error: GitHub username is not configured in config.py.{COLOR_RESET}")
        return
        
    print(f"{COLOR_BLUE}Updating aiuru directly from GitHub...{COLOR_RESET}")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "--force-reinstall", f"git+https://github.com/{GITHUB_USER}/{GITHUB_REPO}.git"]
    try:
        subprocess.check_call(cmd)
        print(f"{COLOR_GREEN}Success! aiuru has been updated to the latest version from GitHub.{COLOR_RESET}")
    except Exception as e:
        print(f"{COLOR_RED}Failed to run pip update: {e}{COLOR_RESET}")
        print(f"{COLOR_YELLOW}Alternatively, you can run: pip install --upgrade git+https://github.com/{GITHUB_USER}/{GITHUB_REPO}.git{COLOR_RESET}")

def print_help_guide():
    print(f"{COLOR_BOLD}Commands:{COLOR_RESET}")
    print("  /help, /h               Show this list of commands")
    print("  /model, /m              Change the active model")
    print("  /quota, /q              View current daily token quota usage")
    print("  /system, /s             Set system prompt (e.g. `/system be brief`) or `/system clear`")
    print("  /save                   Save current chat history (e.g. `/save debug_session`)")
    print("  /load                   Load a saved chat history (e.g. `/load debug_session`)")
    print("  /edit, /e <file> <ins>  Edit/Write file (e.g. `/edit test.py make it print hi`)")
    print("  /clear, /c              Clear current chat history")
    print("  /exit, /x               Exit chatbot")

def main():
    config = load_config()
    args = sys.argv[1:]
    
    if not args:
        sys.argv.append("chat")
    else:
        subcommands = {"setup", "quota", "models", "edit", "ask", "chat", "update", "version"}
        first_arg = args[0]
        
        if first_arg in ("-q", "--quota"):
            sys.argv = [sys.argv[0], "quota"]
        elif first_arg in ("-m", "--model"):
            sys.argv = [sys.argv[0], "models"]
        elif first_arg in ("-l", "--list"):
            sys.argv = [sys.argv[0], "models", "--list-only"]
        elif first_arg in ("-s", "--setup"):
            sys.argv = [sys.argv[0], "setup"]
        elif first_arg in ("-e", "--edit") and len(args) > 1:
            sys.argv = [sys.argv[0], "edit"] + args[1:]
        elif first_arg == "--session":
            sys.argv = [sys.argv[0], "chat"] + args
        elif first_arg in ("-f", "--file", "--system"):
            if sys.stdout.isatty():
                sys.argv = [sys.argv[0], "chat"] + args
            else:
                sys.argv = [sys.argv[0], "ask"] + args
        elif first_arg not in subcommands and not first_arg.startswith("-"):
            if sys.stdout.isatty():
                sys.argv = [sys.argv[0], "chat"] + args
            else:
                sys.argv = [sys.argv[0], "ask"] + args

    parser = argparse.ArgumentParser(
        description=f"{COLOR_CYAN}{COLOR_BOLD}URU AI Space CLI - Professional Developer Assistant{COLOR_RESET}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"aiuru v{__version__}",
        help="Show program's version number and exit"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    subparsers.add_parser("setup", help="Configure URU AI Space API Key")
    subparsers.add_parser("quota", help="Check remaining daily token quota")
    
    models_parser = subparsers.add_parser("models", help="List and select default AI models")
    models_parser.add_argument("--list-only", action="store_true", help="List models without interactive selection")
    
    edit_parser = subparsers.add_parser("edit", help="Edit/Write code directly to a file (Code Assistant Mode)")
    edit_parser.add_argument("file", help="Filepath to write/edit")
    edit_parser.add_argument("instruction", nargs="+", help="Instructions for changes")
    
    ask_parser = subparsers.add_parser("ask", help="Send a quick prompt to the AI (Supports Pipe/STDIN)")
    ask_parser.add_argument("prompt", nargs="*", help="The prompt text")
    ask_parser.add_argument("-f", "--file", help="Attach a local file to the prompt context")
    ask_parser.add_argument("--system", help="Override default system prompt")
    
    chat_parser = subparsers.add_parser("chat", help="Start interactive chatbot session")
    chat_parser.add_argument("--session", help="Load / resume a saved chat session")
    chat_parser.add_argument("initial_prompt", nargs="*", help="Initial prompt to send on startup")
    chat_parser.add_argument("-f", "--file", help="Attach a local file to the initial prompt context")
    chat_parser.add_argument("--system", help="Override system prompt for this session")

    subparsers.add_parser("update", help="Update the CLI tool to the latest version from GitHub")
    subparsers.add_parser("version", help="Show version number and exit")

    if len(args) == 1 and args[0] in ("-h", "--help"):
        parser.print_help()
        return

    parsed_args = parser.parse_args()
    
    if parsed_args.command == "setup":
        run_setup()
        return
    elif parsed_args.command == "update":
        run_self_update()
        return
    elif parsed_args.command == "version":
        print(f"aiuru v{__version__}")
        return

    if not config.get("api_key"):
        print_banner()
        print(f"{COLOR_YELLOW}Welcome! Initial setup required.{COLOR_RESET}")
        config = run_setup()
        if not config or not config.get("api_key"):
            return

    if parsed_args.command == "quota":
        print_quota_info(config)
        
    elif parsed_args.command == "models":
        if parsed_args.list_only:
            api_key = config.get("api_key")
            models = fetch_models_api(api_key)
            if models:
                headers = ["#", "Model ID / Name"]
                rows = [[idx, f"{m['name']} [ID: {m['id']}]"] for idx, m in enumerate(models, 1)]
                draw_table("AVAILABLE MODELS", headers, rows)
            else:
                print(f"{COLOR_RED}Failed to fetch models.{COLOR_RESET}")
        else:
            change_model_interactive(config)
            
    elif parsed_args.command == "edit":
        instruction = " ".join(parsed_args.instruction)
        handle_file_edit(config, parsed_args.file, instruction)
        
    elif parsed_args.command == "ask":
        piped_input = ""
        if not sys.stdin.isatty():
            try:
                piped_input = sys.stdin.read().strip()
            except Exception:
                pass
                
        prompt_parts = []
        if parsed_args.file:
            if os.path.exists(parsed_args.file):
                try:
                    with open(parsed_args.file, "r", encoding="utf-8") as f:
                        content = f.read()
                    filename = os.path.basename(parsed_args.file)
                    prompt_parts.append(f"--- FILE: {filename} ---\n{content}\n--- END OF FILE ---")
                except Exception as e:
                    print(f"{COLOR_RED}Failed to read file {parsed_args.file}: {e}{COLOR_RESET}")
                    return
            else:
                print(f"{COLOR_RED}File not found: {parsed_args.file}{COLOR_RESET}")
                return
                
        if piped_input:
            prompt_parts.append(piped_input)
            
        if parsed_args.prompt:
            prompt_parts.append(" ".join(parsed_args.prompt))
            
        final_prompt = "\n\n".join(prompt_parts)
        if not final_prompt:
            print(f"{COLOR_RED}Please specify a prompt. E.g. aiuru ask \"hello\" or cat file.txt | aiuru ask{COLOR_RESET}")
            return
            
        messages = []
        sys_prompt = parsed_args.system or config.get("system_prompt")
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": final_prompt})
        
        make_completion(config, messages)
        
    elif parsed_args.command == "chat":
        print_banner()
        model_name = config.get("default_model_name", "Unknown Model")
        model_id = config.get("default_model", 1)
        
        chat_history = []
        session_name = parsed_args.session or "autosave"
        
        if parsed_args.session:
            loaded = load_session(parsed_args.session)
            if loaded is not None:
                chat_history = loaded
                print(f"{COLOR_GREEN}Loaded session '{parsed_args.session}' with {len(chat_history)} messages.{COLOR_RESET}")
                
        piped_input = ""
        if not sys.stdin.isatty():
            try:
                piped_input = sys.stdin.read().strip()
                try:
                    sys.stdin = open("/dev/tty")
                except Exception:
                    pass
            except Exception:
                pass
                
        initial_parts = []
        if parsed_args.file:
            if os.path.exists(parsed_args.file):
                try:
                    with open(parsed_args.file, "r", encoding="utf-8") as f:
                        content = f.read()
                    filename = os.path.basename(parsed_args.file)
                    initial_parts.append(f"--- FILE: {filename} ---\n{content}\n--- END OF FILE ---")
                except Exception as e:
                    print(f"{COLOR_RED}Failed to read file {parsed_args.file}: {e}{COLOR_RESET}")
                    return
            else:
                print(f"{COLOR_RED}File not found: {parsed_args.file}{COLOR_RESET}")
                return
                
        if piped_input:
            initial_parts.append(piped_input)
            
        if parsed_args.initial_prompt:
            initial_parts.append(" ".join(parsed_args.initial_prompt))
            
        print(f"{COLOR_BOLD}Current Model:{COLOR_RESET} {COLOR_GREEN}{model_name}{COLOR_RESET} {COLOR_DIM}[ID: {model_id}]{COLOR_RESET}")
        sys_prompt_active = parsed_args.system or config.get("system_prompt")
        if sys_prompt_active:
            print(f"{COLOR_BOLD}System Prompt:{COLOR_RESET} {COLOR_PURPLE}{sys_prompt_active}{COLOR_RESET}")
        print(f"Type {COLOR_CYAN}/help{COLOR_RESET} to show commands, {COLOR_CYAN}Tab{COLOR_RESET} to autocomplete commands.")
        print("-" * 50)
        
        if initial_parts:
            final_initial_prompt = "\n\n".join(initial_parts)
            chat_history.append({"role": "user", "content": final_initial_prompt})
            
            messages = []
            if sys_prompt_active:
                messages.append({"role": "system", "content": sys_prompt_active})
            messages.extend(chat_history)
            
            ai_response = make_completion(config, messages)
            if ai_response:
                chat_history.append({"role": "assistant", "content": ai_response})
                save_session(session_name, chat_history, quiet=True)
            else:
                chat_history.pop()
        
        while True:
            try:
                user_input = input(f"\n{COLOR_GREEN}{COLOR_BOLD}You: {COLOR_RESET}").strip()
                if not user_input:
                    continue
                    
                if user_input.startswith("/"):
                    parts = user_input.split()
                    cmd = parts[0].lower()
                    
                    if cmd in ("/exit", "/quit", "/x"):
                        print(f"{COLOR_YELLOW}Goodbye!{COLOR_RESET}")
                        break
                    elif cmd in ("/help", "/h"):
                        print_help_guide()
                        continue
                    elif cmd in ("/model", "/m"):
                        change_model_interactive(config)
                        config = load_config()
                        print(f"Active Model: {COLOR_GREEN}{config.get('default_model_name')}{COLOR_RESET}")
                        continue
                    elif cmd in ("/quota", "/q"):
                        print_quota_info(config)
                        continue
                    elif cmd in ("/clear", "/c"):
                        chat_history = []
                        save_session(session_name, chat_history, quiet=True)
                        print(f"{COLOR_YELLOW}Chat history cleared.{COLOR_RESET}")
                        continue
                    elif cmd == "/save":
                        if len(parts) < 2:
                            print(f"{COLOR_RED}Please specify a session name. E.g. /save my_session{COLOR_RESET}")
                        else:
                            save_session(parts[1], chat_history)
                            session_name = parts[1]
                        continue
                    elif cmd == "/load":
                        if len(parts) < 2:
                            list_sessions()
                        else:
                            loaded = load_session(parts[1])
                            if loaded is not None:
                                chat_history = loaded
                                session_name = parts[1]
                                print(f"{COLOR_GREEN}Loaded session '{parts[1]}' with {len(chat_history)} messages.{COLOR_RESET}")
                        continue
                    elif cmd in ("/edit", "/e"):
                        if len(parts) < 3:
                            print(f"{COLOR_RED}Usage: /edit <filepath> <instruction>{COLOR_RESET}")
                        else:
                            edit_file = parts[1]
                            edit_instruction = " ".join(parts[2:])
                            handle_file_edit(config, edit_file, edit_instruction)
                        continue
                    elif cmd in ("/system", "/s"):
                        if len(parts) < 2:
                            current = config.get("system_prompt")
                            if current:
                                print(f"Current System Prompt: {COLOR_PURPLE}{current}{COLOR_RESET}")
                            else:
                                print("No system prompt set.")
                        else:
                            sub_cmd = " ".join(parts[1:])
                            if sub_cmd.lower() in ("clear", "reset"):
                                config["system_prompt"] = ""
                                save_config(config)
                                print(f"{COLOR_YELLOW}System prompt cleared.{COLOR_RESET}")
                            else:
                                config["system_prompt"] = sub_cmd
                                save_config(config)
                                print(f"{COLOR_GREEN}System prompt set to: {COLOR_PURPLE}{sub_cmd}{COLOR_RESET}")
                        continue
                    else:
                        print(f"{COLOR_RED}Unknown command: {cmd}. Type /help for assistance.{COLOR_RESET}")
                        continue
                
                chat_history.append({"role": "user", "content": user_input})
                
                messages = []
                sys_prompt_active = config.get("system_prompt")
                if sys_prompt_active:
                    messages.append({"role": "system", "content": sys_prompt_active})
                messages.extend(chat_history)
                
                ai_response = make_completion(config, messages)
                if ai_response:
                    chat_history.append({"role": "assistant", "content": ai_response})
                    save_session(session_name, chat_history, quiet=True)
                else:
                    chat_history.pop()
                    
            except KeyboardInterrupt:
                print(f"\n{COLOR_YELLOW}Goodbye!{COLOR_RESET}")
                break
            except EOFError:
                print(f"\n{COLOR_YELLOW}Goodbye!{COLOR_RESET}")
                break

if __name__ == "__main__":
    main()
