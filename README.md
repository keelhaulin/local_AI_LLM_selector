
# 🧠 LLM Model Selector (Web UI + Docker)

A simple, intuitive web-based tool to help you choose the best Large Language Model (LLM) variant for **local inference** based on:
- Use case (chat, code, rag, thinking)
- Hardware specs (GPU VRAM, context window)
- Performance needs (tokens per minute)
- Optimization features (Flash Attention, KV Cache)

Built with [Flask](https://flask.palletsprojects.com/) and runs easily via Docker.

## 📦 Features

- ✅ Web UI (access from any browser)
- ✅ Suggests top 10 model variants
- ✅ Optional toggles for Flash Attention & KV Cache
- ✅ Dockerized for easy deployment
- ✅ Extendable for Hugging Face integration or Ollama setup

## 🗂️ Folder Structure

```
llm_model_selector_web/
├── app.py               # Main Flask web app
├── Dockerfile           # Docker setup for running the web app
├── requirements.txt     # Python package dependencies
└── README.md            # You're reading it!
```

## 🚀 Quick Start (Docker)

```bash
git clone https://github.com/yourusername/llm_model_selector_web.git
cd llm_model_selector_web

docker build -t model-selector .
docker run -d -p 8500:8500 --name model-selector model-selector
```

Then open your browser at: [http://localhost:8500](http://localhost:8500)

## 📥 Requirements (if running locally)

```bash
pip install flask
python app.py
```

## 🔮 Planned Features

- Hugging Face model search and links
- Ollama-compatible GGUF recommendations
- LM Studio integration
- Local model loader helper

## 🤝 Contributing

Contributions welcome! Fork the repo, make changes, and submit a pull request.

## 📄 License

MIT License. Use freely with attribution.
