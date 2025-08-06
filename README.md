Ollama CLI:

set OLLAMA_HOST=0.0.0.0

set OLLAMA_PORT=11434

ollama serve



https://ollama.com/

# Python-Ollama GUI

A sleek and intuitive desktop application that brings the power of open-source language models to your fingertips.

Python-Ollama GUI provides a user-friendly interface to interact with various AI models through Ollama, featuring real-time response streaming, adjustable parameters, and support for models ranging from the efficient Mistral (7B) to the more powerful OpenAI (20B).

Perfect for developers, writers, and AI enthusiasts who want to harness AI capabilities without dealing with command-line interfaces.

![Python-Ollama GUI](screenshot.png) *(Add a screenshot of your application)*

## Features

- 🎯 Clean and intuitive graphical user interface
- 🔄 Real-time streaming responses
- 🎛️ Adjustable parameters (temperature, max tokens)
- 📝 Support for system messages and user prompts
- 🛑 Ability to stop generation mid-stream
- 🎨 Markdown-style formatting in responses
- 📊 Multiple model support:
  - Mistral 7B (7B, 4.1GB)
  - DeepSeek R1 (8B, 5.2GB)
  - OpenAI GPT-OSS-20B (20B, 14GB)

## Prerequisites

- Python 3.6+
- Ollama server running locally or on a remote machine
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/Python-Ollama-Public.git
cd Python-Ollama-Public
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on the provided `.env-example`:
```bash
cp .env-example .env
```

4. Edit the `.env` file with your Ollama server details:
```
API_IP=127.0.0.1  # Use your Ollama server IP
PORT=11434        # Default Ollama port
```

## Usage

1. Start the application:
```bash
python main.py
```

2. Configure your generation settings:
   - Select a model from the dropdown menu
   - Adjust temperature (higher = more creative, lower = more focused)
   - Set maximum tokens for response length
   - Enter a system message to guide the AI's behavior
   - Type your prompt in the user message field

3. Click "Generate" to start text generation
   - Use the "Stop" button to halt generation at any time
   - Generated text will appear in the response area with markdown formatting

## Configuration

The application can be configured through the `.env` file:
- `API_IP`: IP address of your Ollama server
- `PORT`: Port number of your Ollama server (default: 11434)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Built with Python and Tkinter
- Powered by Ollama
- Uses various open-source language models 
