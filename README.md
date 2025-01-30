On Ollama PC CMD/Terminal if you want port 11435 to be used:
set OLLAMA_ADDRESS=0.0.0.0:11435
set OLLAMA_HOST=http://0.0.0.0:11435
ollama serve

main.py
Line 61+ :
Add your AI models
left side of comma: name for drop-down menu
right side of comma: modelID

on Remote PC:
pip install -r requirements.txt
change .env-example to .env and add your API_IP and PORT
python main.py
