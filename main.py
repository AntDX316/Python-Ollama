import os
import json
import time
import requests
import threading
import atexit
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from dotenv import load_dotenv

# Load the environment variables from .env
load_dotenv()

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ollama Response Streamer")
        self.root.geometry("800x600")

        # ----- Basic style setup for a simple, system-like look -----
        style = ttk.Style(root)
        style.theme_use('clam')  # or 'default', 'alt', 'classic', etc.

        # A basic button style that only changes font & padding
        style.configure(
            "Basic.TButton",
            font=("Helvetica", 12, "bold"),
            padding=8
        )
        # Slight hover effect (optional)
        style.map(
            "Basic.TButton",
            background=[("active", "#DDDDDD")]
        )

        # Frame & label styling for minimal look
        style.configure("MainFrame.TFrame", background="#f0f0f0")
        style.configure("MainLabel.TLabel", background="#f0f0f0", font=("Helvetica", 14))
        # ------------------------------------------------------------

        # Bind cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)

        # Main frame
        self.main_frame = ttk.Frame(self.root, style="MainFrame.TFrame", padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # System Message label
        system_label = ttk.Label(self.main_frame, text="System Message:", style="MainLabel.TLabel")
        system_label.pack(pady=(0,5))

        # System Message input
        self.system_input = tk.Text(self.main_frame, height=2, font=("TkDefaultFont", 12))
        self.system_input.pack(fill=tk.X, pady=(0, 10))
        self.system_input.insert("1.0", "You are a helpful AI assistant.")

        # User Message label
        self.prompt_label = ttk.Label(self.main_frame, text="User Message:", style="MainLabel.TLabel")
        self.prompt_label.pack(pady=(0,5))

        # Prompt input
        self.prompt_input = tk.Text(self.main_frame, height=3, font=("TkDefaultFont", 12))
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert("1.0", "Write 200 things a CEO can do")

        # Parameters frame
        self.params_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.params_frame.pack(pady=(0, 10))

        # Temperature control
        temp_label = ttk.Label(self.params_frame, text="Temperature:", style="MainLabel.TLabel")
        temp_label.pack(side=tk.LEFT, padx=(0, 5))
        self.temperature_var = tk.StringVar(value="0.7")
        self.temperature_entry = ttk.Entry(self.params_frame, textvariable=self.temperature_var, width=6)
        self.temperature_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Max Tokens control
        tokens_label = ttk.Label(self.params_frame, text="Max Tokens:", style="MainLabel.TLabel")
        tokens_label.pack(side=tk.LEFT, padx=(0, 5))
        self.max_tokens_var = tk.StringVar(value="8192")
        self.max_tokens_entry = ttk.Entry(self.params_frame, textvariable=self.max_tokens_var, width=6)
        self.max_tokens_entry.pack(side=tk.LEFT)

        # Models, sorted by ascending GB
        # (DisplayString, modelID)
        self.models = [
            ("Mistral 7B (7B, 4.1GB)",      "mistral"),
            ("DeepSeek R1 (8B, 5.2GB)",     "deepseek-r1"),
            ("OpenAI GPT-OSS (20B, 14GB)",       "gpt-oss")
        ]
        self.selected_model = tk.StringVar(value=self.models[0][0])  # default to first

        # Model dropdown label
        model_label = ttk.Label(self.main_frame, text="Select model:", style="MainLabel.TLabel")
        model_label.pack()

        # Model dropdown
        self.model_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.selected_model,
            values=[m[0] for m in self.models],
            state="readonly",
            font=("TkDefaultFont", 12),
            width=30  # Make the dropdown wider
        )
        self.model_dropdown.pack(pady=(0,10))

        # Button frame
        self.button_frame = ttk.Frame(self.main_frame, style="MainFrame.TFrame")
        self.button_frame.pack(pady=(0, 10))

        # Generate button
        self.generate_button = ttk.Button(
            self.button_frame,
            text="Generate",
            command=self.start_generation,
            style="Basic.TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Stop button
        self.stop_button = ttk.Button(
            self.button_frame,
            text="Stop",
            command=self.stop_generation,
            state=tk.DISABLED,
            style="Basic.TButton"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Response area
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
        self.displayed_length = 0
        self.is_generating = False
        self.current_response = None

    def start_generation(self):
        self.generate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        # Clear old response
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
            # Load the IP from .env
            api_ip = os.getenv("API_IP", "127.0.0.1")  # default if missing
            port = os.getenv("PORT", "11434")  # default Ollama port if missing
            url = f"http://{api_ip}:{port}/api/generate"

            # Resolve the actual model name from the user's selection
            chosen_label = self.selected_model.get()
            selected_model_id = next(item[1] for item in self.models if item[0] == chosen_label)

            data = {
                "model": selected_model_id,
                "prompt": self.prompt_input.get("1.0", tk.END).strip(),
                "system": self.system_input.get("1.0", tk.END).strip(),
                "temperature": float(self.temperature_var.get()),
                "num_predict": int(self.max_tokens_var.get())
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
                # heading
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

        # If user was at bottom, keep them at bottom
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