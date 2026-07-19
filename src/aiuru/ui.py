import sys
import time
import threading

# ANSI color codes for premium look
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_DIM = "\033[90m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_PURPLE = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_WHITE = "\033[37m"

def print_banner():
    banner = f"""{COLOR_CYAN}{COLOR_BOLD}
   __    ___   _  _   ____   _  _ 
  /__\\  (_ _) ( )( ) (  _ \\ ( )( )
 /(__)\\  _|_   )(__(  )   /  )(__(
(__)(__)(___) (____) (_)\\_  (____) {COLOR_RESET}{COLOR_DIM}v2.0 (Real CLI Edition){COLOR_RESET}
{COLOR_DIM}URU AI Space CLI - Professional developer tool. Type TAB for autocomplete.{COLOR_RESET}
"""
    print(banner)

def draw_table(title, headers, rows):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            stripped_val = str(val)
            for color in (COLOR_RESET, COLOR_BOLD, COLOR_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_PURPLE, COLOR_CYAN, COLOR_WHITE):
                stripped_val = stripped_val.replace(color, "")
            col_widths[idx] = max(col_widths[idx], len(stripped_val))
            
    total_table_width = sum(col_widths) + 3 * len(headers) + 1
    border = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    if title:
        padding = (total_table_width - len(title) - 2) // 2
        print(f"{COLOR_CYAN}+" + "-" * (total_table_width - 2) + f"+{COLOR_RESET}")
        print(f"{COLOR_CYAN}|" + " " * padding + f"{COLOR_BOLD}{COLOR_WHITE}{title}{COLOR_RESET}" + " " * (total_table_width - len(title) - padding - 2) + f"{COLOR_CYAN}|{COLOR_RESET}")
        
    print(COLOR_CYAN + border + COLOR_RESET)
    header_line = "|" + "|".join([f" {COLOR_BOLD}{COLOR_WHITE}{headers[idx].ljust(col_widths[idx])}{COLOR_RESET} " for idx in range(len(headers))]) + "|"
    print(header_line)
    print(COLOR_CYAN + border + COLOR_RESET)
    
    for row in rows:
        formatted_cols = []
        for idx, val in enumerate(row):
            val_str = str(val)
            stripped_val = val_str
            for color in (COLOR_RESET, COLOR_BOLD, COLOR_DIM, COLOR_RED, COLOR_GREEN, COLOR_YELLOW, COLOR_BLUE, COLOR_PURPLE, COLOR_CYAN, COLOR_WHITE):
                stripped_val = stripped_val.replace(color, "")
            diff_len = len(val_str) - len(stripped_val)
            formatted_cols.append(val_str.ljust(col_widths[idx] + diff_len))
        print("|" + "|".join([f" {c} " for c in formatted_cols]) + "|")
        
    print(COLOR_CYAN + border + COLOR_RESET)

class Spinner:
    def __init__(self, message="Thinking..."):
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.message = message
        self.stop_running = False
        self._thread = None

    def start(self):
        if not sys.stderr.isatty():
            return
        self.stop_running = False
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()

    def _spin(self):
        idx = 0
        while not self.stop_running:
            sys.stderr.write(f"\r{COLOR_CYAN}{self.spinner_chars[idx]} {COLOR_DIM}{self.message}{COLOR_RESET}")
            sys.stderr.flush()
            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(0.08)

    def stop(self):
        if not sys.stderr.isatty():
            return
        self.stop_running = True
        if self._thread:
            self._thread.join()
        sys.stderr.write("\r" + " " * 40 + "\r")
        sys.stderr.flush()
