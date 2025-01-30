import tkinter as tk
from tkinter import ttk
import requests
import json
import threading
import time
import atexit
from tkinter import scrolledtext

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Response Streamer")
        self.root.geometry("800x600")

        # ----- BASIC STYLE CONFIG -----
        style = ttk.Style(root)
        # Try using a simple theme:
        style.theme_use('clam')  # or 'alt', 'default', etc.

        # Create a style with no forced background/foreground,
        # so it uses the system default look. We only set font & padding.
        style.configure(
            "Basic.TButton",
            font=("Helvetica", 12, "bold"),
            padding=8
        )
        # Slightly lighter on hover (optional)
        style.map(
            "Basic.TButton",
            background=[("active", "#DDDDDD")]
        )

        # Frame & label styles for a minimal look
        style.configure("MainFrame.TFrame", background="#f0f0f0")
        style.configure("MainLabel.TLabel", background="#f0f0f0", font=("Helvetica", 14))
        # ---------------------------------------

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)

        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame", padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.prompt_label = ttk.Label(self.main_frame, text="Enter your prompt:", style="MainLabel.TLabel")
        self.prompt_label.pack(pady=(0,5))

        self.prompt_input = tk.Text(self.main_frame, height=3, font=("TkDefaultFont", 12))
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert("1.0", "Write 200 things a CEO can do")

        # Example model list
        self.models = [
            ("Llama 3.2 (3B, 2.0GB)",    "llama3.2"),
            ("DeepSeek (7B, 4.7GB)",     "deepseek-r1"),
            ("Gemma 2 (7B, 5.0GB)",      "gemma2"),
            ("Phi4 (14B, 9.1GB)",        "phi4"),
            ("Mistral (24B, 14GB)",      "mistral-small:24b")
        ]
        self.selected_model = tk.StringVar(value=self.models[0][0])

        model_label = ttk.Label(self.main_frame, text="Select model:", style="MainLabel.TLabel")
        model_label.pack()

        self.model_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.selected_model,
            values=[m[0] for m in self.models],
            state="readonly",
            font=("TkDefaultFont", 12)
        )
        self.model_dropdown.pack(pady=(0,10))

        self.button_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.button_frame.pack(pady=(0, 10))

        self.generate_button = ttk.Button(
            self.button_frame, text="Generate",
            command=self.start_generation,
            style="Basic.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(
            self.button_frame, text="Stop",
            command=self.stop_generation,
            state=tk.DISABLED,
            style="Basic.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.response_area = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            height=20,
            font=("TkDefaultFont", 12)
        )
        self.response_area.pack(fill=tk.BOTH, expand=True)
        self.response_area.config(state=tk.DISABLED)

        # Markdown-like tags
        self.response_area.tag_configure("bold", font=("TkDefaultFont", 12, "bold"))
        self.response_area.tag_configure("italic", font=("TkDefaultFont", 12, "italic"))
        self.response_area.tag_configure("heading", font=("TkDefaultFont", 15, "bold"))
        self.response_area.tag_configure("code", font=("Courier", 12))

        self.accumulated_response = ""
        self.is_generating = False
        self.current_response = None
        self.displayed_length = 0

    def start_generation(self):
        self.generate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.response_area.config(state=tk.NORMAL)
        self.response_area.delete("1.0", tk.END)
        self.response_area.config(state=tk.DISABLED)
        self.accumulated_response = ""
        self.displayed_length = 0
        threading.Thread(target=self.generate_response, daemon=True).start()

    def generate_response(self):
        self.is_generating = True
        accumulated_chars = 0
        last_update_time = time.time()

        try:
            url = "http://74.102.26.111:11434/api/generate"

            chosen_label = self.selected_model.get()
            # find the ID from that display text
            selected_model_id = next(item[1] for item in self.models if item[0] == chosen_label)

            data = {
                "model": selected_model_id,
                "prompt": self.prompt_input.get("1.0", tk.END).strip()
            }
            self.current_response = requests.post(url, json=data, stream=True)

            for line in self.current_response.iter_lines():
                if not self.is_generating:
                    break
                if line:
                    json_line = json.loads(line)
                    response_fragment = json_line.get("response", "")
                    self.accumulated_response += response_fragment
                    accumulated_chars += len(response_fragment)

                    current_time = time.time()
                    if accumulated_chars >= 50 or (current_time - last_update_time) >= 0.5:
                        self.display_new_content()
                        accumulated_chars = 0
                        last_update_time = current_time

        except Exception as e:
            self.response_area.config(state=tk.NORMAL)
            self.response_area.insert(tk.END, f"\nError: {str(e)}")
            self.response_area.config(state=tk.DISABLED)
        finally:
            if accumulated_chars > 0:
                self.display_new_content()

            self.is_generating = False
            self.current_response = None
            self.generate_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def display_new_content(self):
        new_text = self.accumulated_response[self.displayed_length:]
        if not new_text:
            return

        self.append_markdown(new_text)
        self.displayed_length = len(self.accumulated_response)

    def append_markdown(self, text):
        yview_before = self.response_area.yview()
        at_bottom = (yview_before[1] >= 0.99)

        lines = text.split('\n')

        self.response_area.config(state=tk.NORMAL)
        for idx, line in enumerate(lines):
            suffix = '\n' if (idx < len(lines) - 1) else ''

            if line.startswith('#'):
                count = len(line.split()[0])
                heading_text = line[count:].strip()
                self.response_area.insert(tk.END, heading_text + suffix, "heading")
            elif '**' in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        self.response_area.insert(tk.END, part, "bold")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, suffix)
            elif '`' in line:
                parts = line.split('`')
                for i, part in enumerate(parts):
                    if i % 2 == 1:
                        self.response_area.insert(tk.END, part, "code")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, suffix)
            else:
                self.response_area.insert(tk.END, line + suffix)

        if at_bottom:
            self.response_area.see(tk.END)

        self.response_area.config(state=tk.DISABLED)

    def stop_generation(self):
        self.is_generating = False
        if self.current_response:
            try:
                self.current_response.close()
            except:
                pass
        self.stop_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.NORMAL)
        self.response_area.config(state=tk.NORMAL)
        self.response_area.insert(tk.END, "\n[Generation stopped by user]")
        self.response_area.config(state=tk.DISABLED)

    def cleanup(self):
        if self.current_response:
            try:
                self.current_response.close()
            except:
                pass
        self.is_generating = False

    def on_closing(self):
        self.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()