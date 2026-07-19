import os
import difflib
from .ui import (
    COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_CYAN, COLOR_BOLD, COLOR_RESET, COLOR_BLUE
)
from .api import make_completion

def extract_code_block(response_text):
    start_marker = "```"
    first_idx = response_text.find(start_marker)
    if first_idx == -1:
        return response_text.strip()
        
    line_end = response_text.find("\n", first_idx)
    if line_end == -1:
        return response_text[first_idx + 3:].strip()
        
    close_idx = response_text.find(start_marker, line_end)
    if close_idx == -1:
        return response_text[line_end + 1:].strip()
        
    return response_text[line_end + 1:close_idx].strip()

def show_diff_and_confirm(filepath, old_content, new_content):
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=filepath,
        tofile=filepath + " (updated)",
        n=3
    ))
    
    if not diff:
        print(f"{COLOR_YELLOW}No changes detected.{COLOR_RESET}")
        return False
        
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}Proposed Changes:{COLOR_RESET}")
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            print(f"{COLOR_GREEN}{line}{COLOR_RESET}", end="")
        elif line.startswith('-') and not line.startswith('---'):
            print(f"{COLOR_RED}{line}{COLOR_RESET}", end="")
        elif line.startswith('@@'):
            print(f"{COLOR_CYAN}{line}{COLOR_RESET}", end="")
        else:
            print(line, end="")
    print()
    
    try:
        confirm = input(f"{COLOR_YELLOW}Apply these changes? (y/N): {COLOR_RESET}").strip().lower()
        if confirm in ('y', 'yes'):
            if old_content:
                backup = filepath + ".bak"
                with open(backup, "w", encoding="utf-8") as f:
                    f.write(old_content)
                backup_msg = f" Backup saved to {os.path.basename(backup)}."
            else:
                backup_msg = ""
                
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"{COLOR_GREEN}Success! File updated.{backup_msg}{COLOR_RESET}")
            return True
        else:
            print(f"{COLOR_YELLOW}Changes discarded.{COLOR_RESET}")
            return False
    except (KeyboardInterrupt, EOFError):
        print(f"\n{COLOR_YELLOW}Changes discarded.{COLOR_RESET}")
        return False

def handle_file_edit(config, filepath, instruction):
    if not os.path.exists(filepath):
        old_content = ""
        print(f"{COLOR_YELLOW}File '{filepath}' not found. Creating new file.{COLOR_RESET}")
    else:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                old_content = f.read()
        except Exception as e:
            print(f"{COLOR_RED}Error reading file: {e}{COLOR_RESET}")
            return False

    system_prompt = (
        "You are an expert software developer. Your task is to edit/write the provided file "
        "according to the user's instructions. Return ONLY the updated file contents. "
        "Do not include any explanation, introduction, or wrap-up. "
        "Start the output directly with a code block containing the full file contents, like:\n"
        "```python\n"
        "# code here\n"
        "```"
    )
    
    prompt = f"Target File: {filepath}\n"
    if old_content:
        prompt += f"--- CURRENT FILE CONTENT ---\n{old_content}\n--- END OF FILE CONTENT ---\n"
    else:
        prompt += "--- FILE IS CURRENTLY EMPTY ---\n"
        
    prompt += f"Instructions: {instruction}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    print(f"{COLOR_BLUE}Generating changes for {filepath}...{COLOR_RESET}")
    raw_response = make_completion(config, messages, quiet=True)
    if not raw_response:
        print(f"{COLOR_RED}Failed to get response from AI.{COLOR_RESET}")
        return False
        
    new_content = extract_code_block(raw_response)
    return show_diff_and_confirm(filepath, old_content, new_content)
