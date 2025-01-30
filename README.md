# Python Ollama GUI

The Python Ollama GUI is a sleek, user-friendly desktop application that lets you interact with Ollama's AI models across your local network.

It features a clean interface with a text input area, model selection dropdown, and real-time response streaming.

The app allows you to run Ollama on one machine and access it remotely from another computer on your network, making it perfect for users who want to leverage their powerful GPU machine while working from a different device.

With support for various models like Llama, DeepSeek, Gemma, Phi4, and Mistral, it provides a convenient way to generate AI responses without the complexity of command-line interfaces.

## Server Setup (Ollama PC)

1. Open CMD/Terminal and run these commands to configure Ollama for network access:
```bash
set OLLAMA_ADDRESS=0.0.0.0:11434
set OLLAMA_HOST=http://0.0.0.0:11434
ollama serve
```

## Client Setup (Remote PC)

1. Clone and install dependencies:
```bash
git clone https://github.com/yourusername/Python-Ollama.git
cd Python-Ollama
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env-example .env
```
Edit `.env` file and set:
- `API_IP`: IP address of your Ollama server
- `PORT`: Port number (default: 11434)

3. Start the application:
```bash
python main.py
```

## Customizing Models

To add or modify AI models, edit `main.py` around line 61. The format is:
```python
self.models = [
    ("Display Name", "model_id"),
    ("Llama 3.2 (3B, 2.0GB)", "llama3.2"),
    # Add more models here
]
```
- Left side: Name shown in dropdown menu
- Right side: Ollama model ID

## Features

- 🖥️ Client-server architecture for network access
- 🎯 Clean, modern Tkinter interface
- 🤖 Support for multiple Ollama models
- 💨 Real-time response streaming
- 🛑 Stop generation at any time
- 🎨 Markdown-style formatting support

## Requirements

- Python 3.x
- Ollama installed on server machine
- Network connectivity between client and server
- Required Python packages (see `requirements.txt`)

## License

This project is licensed under the MIT License.
