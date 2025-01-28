import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import threading

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Response Streamer")
        self.root.geometry("800x600")

        # Create main container
        self.main_frame = tk.Frame(self.root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create and pack the prompt label
        self.prompt_label = tk.Label(self.main_frame, text="Enter your prompt:")
        self.prompt_label.pack(pady=(0, 5))

        # Create and pack the prompt input
        self.prompt_input = tk.Text(self.main_frame, height=3)
        self.prompt_input.pack(fill=tk.X, pady=(0, 10))
        self.prompt_input.insert("1.0", "Write 200 things a CEO can do")

        # Create and pack the generate button
        self.generate_button = tk.Button(self.main_frame, text="Generate", command=self.start_generation)
        self.generate_button.pack(pady=(0, 10))

        # Create and pack the response text area
        self.response_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.response_area.pack(fill=tk.BOTH, expand=True)

    def generate_response(self):
        # Clear previous response
        self.response_area.delete("1.0", tk.END)
        self.generate_button.config(state=tk.DISABLED)

        try:
            # Define the API endpoint and payload
            url = "http://74.102.26.111:11434/api/generate"
            data = {
                "model": "deepseek-r1",
                "prompt": self.prompt_input.get("1.0", tk.END).strip()
            }

            # Send the POST request
            response = requests.post(url, json=data, stream=True)

            for line in response.iter_lines():
                if line:
                    # Parse each JSON line
                    json_line = json.loads(line)
                    # Extract the response fragment
                    response_fragment = json_line.get("response", "")
                    
                    # Update the text widget
                    self.response_area.insert(tk.END, response_fragment)
                    self.response_area.see(tk.END)  # Auto-scroll to the bottom
                    
                    # Update the GUI
                    self.root.update()

        except Exception as e:
            self.response_area.insert(tk.END, f"\nError: {str(e)}")
        
        finally:
            self.generate_button.config(state=tk.NORMAL)

    def start_generation(self):
        # Start generation in a separate thread to prevent GUI freezing
        threading.Thread(target=self.generate_response, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()
