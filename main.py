import tkinter as tk
from tkinter import scrolledtext, font
import requests
import json
import threading
import markdown
from tkinter import ttk
import atexit

class AIGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Response Streamer")
        self.root.geometry("800x600")

        # Bind cleanup to window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        atexit.register(self.cleanup)  # Register cleanup for Python exit

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

        # Create button frame for generate and stop buttons
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(pady=(0, 10))

        # Create and pack the generate button
        self.generate_button = tk.Button(self.button_frame, text="Generate", command=self.start_generation)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Create and pack the stop button
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_generation, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # Create and pack the response text area
        self.response_area = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, height=20)
        self.response_area.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for markdown styling
        self.response_area.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))
        self.response_area.tag_configure("italic", font=("TkDefaultFont", 10, "italic"))
        self.response_area.tag_configure("heading", font=("TkDefaultFont", 12, "bold"))
        self.response_area.tag_configure("code", font=("Courier", 10))
        
        # Store the accumulated response
        self.accumulated_response = ""
        self.last_line_count = 0
        
        # Flag to control generation and store response object
        self.is_generating = False
        self.current_response = None

    def apply_markdown_styling(self, text):
        # Get current scroll position
        current_scroll = self.response_area.yview()
        
        # Get current height
        current_height = self.response_area.count("1.0", tk.END, "lines")
        
        # Clear the text widget
        self.response_area.delete("1.0", tk.END)
        
        # Simple markdown parsing and styling
        lines = text.split('\n')
        for line in lines:
            # Handle headers
            if line.startswith('#'):
                count = len(line.split()[0])  # Count the number of #
                text = line[count:].strip()
                self.response_area.insert(tk.END, text + '\n', "heading")
            
            # Handle bold text
            elif '**' in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are bold
                        self.response_area.insert(tk.END, part, "bold")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, '\n')
            
            # Handle code blocks
            elif line.startswith('```') or line.endswith('```'):
                continue  # Skip the delimiter lines
            elif '`' in line:
                parts = line.split('`')
                for i, part in enumerate(parts):
                    if i % 2 == 1:  # Odd indices are code
                        self.response_area.insert(tk.END, part, "code")
                    else:
                        self.response_area.insert(tk.END, part)
                self.response_area.insert(tk.END, '\n')
            
            # Regular text
            else:
                self.response_area.insert(tk.END, line + '\n')
        
        # Get new height
        new_height = self.response_area.count("1.0", tk.END, "lines")
        
        # If content has grown, auto-scroll to bottom
        if new_height > current_height:
            self.response_area.see(tk.END)
        else:
            # Otherwise maintain the previous scroll position
            self.response_area.yview_moveto(current_scroll[0])

    def stop_generation(self):
        self.is_generating = False
        if self.current_response:
            try:
                self.current_response.close()  # Close the connection to stop server-side generation
            except:
                pass
            self.current_response = None
        self.stop_button.config(state=tk.DISABLED)
        self.generate_button.config(state=tk.NORMAL)
        self.response_area.insert(tk.END, "\n[Generation stopped by user]")

    def generate_response(self):
        # Clear previous response
        self.accumulated_response = ""
        self.response_area.delete("1.0", tk.END)
        self.generate_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_generating = True

        try:
            # Define the API endpoint and payload
            url = "http://74.102.26.111:11434/api/generate"
            data = {
                "model": "mistral-small:24b",
                "prompt": self.prompt_input.get("1.0", tk.END).strip()
            }

            # Send the POST request and store the response object
            self.current_response = requests.post(url, json=data, stream=True)

            for line in self.current_response.iter_lines():
                if not self.is_generating:  # Check if we should stop
                    break
                    
                if line:
                    # Parse each JSON line
                    json_line = json.loads(line)
                    # Extract the response fragment
                    response_fragment = json_line.get("response", "")
                    
                    # Accumulate the response
                    self.accumulated_response += response_fragment
                    
                    # Apply markdown styling
                    self.apply_markdown_styling(self.accumulated_response)
                    
                    # Update the GUI
                    self.root.update()

        except Exception as e:
            self.response_area.insert(tk.END, f"\nError: {str(e)}")
        
        finally:
            self.is_generating = False
            self.current_response = None
            self.generate_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def start_generation(self):
        # Start generation in a separate thread to prevent GUI freezing
        threading.Thread(target=self.generate_response, daemon=True).start()

    def cleanup(self):
        """Clean up resources when the application exits"""
        if self.current_response:
            try:
                self.current_response.close()
            except:
                pass
            self.current_response = None
        self.is_generating = False

    def on_closing(self):
        """Handle window closing event"""
        self.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AIGUI(root)
    root.mainloop()
