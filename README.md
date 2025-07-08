# ARA (Artificial Rulings Assistant)

Welcome to **ARA** — your AI-powered assistant for all things Starfinder! ARA leverages state-of-the-art LLMs and a curated context database to answer your Starfinder rules, lore, and gameplay questions with speed and accuracy.

---

## 🚀 Quick Start (with Docker Compose)

ARA is designed for effortless local setup using Docker Compose. This spins up both the Flask-based ARA server and an [Ollama](https://ollama.com/) container for local LLM inference.

### **Requirements**
- Python3: to install, run the following commands
```bash
sudo apt update
sudo apt install python3 python3-pip
```
- Docker: version used is Docker Desktop, with comes with compose pre-installed. Will update documentation for a non Desktop version soon.

### **1. Clone the Repository**

```bash
git clone https://github.com/EpsilonN7/ARA.git
cd ARA/ara_core/ara_docker
```

> **Note:** All the following commands should be run from the `ara_core/ara_docker` directory.

---

### **2. Prepare Your Configuration (Optional)**

- `config.yaml` controls which Ollama model is used and what sources ARA references.
- By default, it uses `llama3.2:3b`. You can change this after importing your own models.

---

### **3. Launch the Stack**

```bash
docker compose up --build
```

- This will:
  - Build the ARA Flask app image.
  - Start the Flask server on **port 6749** (mapped to your host).
  - Start Ollama on **port 11434** with GPU acceleration enabled (if available).
  - Persist Ollama models in a named volume (`ollama_models`).

---

### **4. Visual Overview**

Below is a visual diagram of the Docker Compose setup:

```
┌────────────────────────────────────────────────────────────┐
│                      Docker Host                          │
│                                                            │
│  ┌─────────────────────────────┐   ┌────────────────────┐  │
│  │        flask (ARA)          │   │     ollama         │  │
│  │  - Python + Flask           │   │  - LLM Engine      │  │
│  │  - Port: 6749               │   │  - Port: 11434     │  │
│  │  - Mounts: ./app (code)     │   │  - Models:         │  │
│  │  - CONFIG_PATH=config.yaml  │   │    ollama_models   │  │
│  └─────────────▲───────────────┘   └──────────▲─────────┘  │
│                │                               │           │
│      Requests  │     HTTP (llm queries)        │           │
│     from user  └─────────────►─────────────────┘           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

- **ARA Flask**: Handles web requests, processes questions, manages scraping and context.
- **Ollama**: Runs your selected Large Language Model for inference.
- **ollama_models volume**: Ensures downloaded/custom models persist across container restarts.

---

## 🧠 Loading a Custom Ollama Model

You can add or switch models in the running Ollama container using the Linux command line.

### **A. Pull a Model from Ollama Hub**

To download a new model (e.g., `llama3`):

```bash
docker exec -it ara_docker-ollama-1 ollama pull llama3
```

> - Replace `ara_docker-ollama-1` with your actual Ollama container name (run `docker ps` to check).
> - The model will persist in the `ollama_models` Docker volume.

### **B. Import a Local Custom Model**

1. **Copy your model file** (e.g., `MyModel.gguf`) into the volume:

   ```bash
   docker cp /path/to/MyModel.gguf ara_docker-ollama-1:/root/.ollama/models
   ```

2. **(Optional) Register the model:**  
   If your model requires registration, use the [Ollama CLI](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) inside the container:

   ```bash
   docker exec -it ara_docker-ollama-1 bash
   # Inside container:
   ollama create mymodel -f /root/.ollama/models/MyModel.gguf
   ```

3. **Update `config.yaml`:**  
   Change the `model:` field to the name/tag of your custom model.

   ```yaml
   model: mymodel
   ```

4. **Restart the stack:**

   ```bash
   docker compose down
   docker compose up --build
   ```

---

## 🛠️ Configuration Reference

- **`config.yaml`**
  - `model`: The Ollama model to use (e.g., `llama3.2:3b`, `mymodel`).
  - `ai_host`: Should point to `http://ollama:11434` unless you run Ollama elsewhere.
  - `port`: The port for Flask (default: `6749`).
  - `sources`: List of URLs ARA scrapes or references for context.

---

## 📝 Example Usage

- With everything running, run the following commands
---

## 🔍 Troubleshooting

- **GPU issues?**  
  Make sure you have the `nvidia-container-toolkit` installed and working.  
  Otherwise, edit `docker-compose.yaml` to remove `runtime: nvidia` and the `NVIDIA_VISIBLE_DEVICES` line.
- **Model not found?**  
  Make sure you have pulled or imported the correct model, and that its name matches `config.yaml`.

---

## 📚 Further Reading

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Starfinder Archives of Nethys](https://www.aonsrd.com/)

---

## 🏗️ Development

- The Flask server and supporting code are in `ara_core/ara_docker`.
- To develop or debug, use the included `debugging/` artifacts and logs.

---

## 💬 Questions / Feedback

Open an issue or discussion on [GitHub](https://github.com/EpsilonN7/ARA/issues).

---

**ARA** is open source and in active development. Enjoy exploring the galaxy with AI at your side!
