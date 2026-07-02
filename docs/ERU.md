# Eru - Rivendell Forensic AI Models

This directory contains Ollama Modelfiles for creating Eru, the Rivendell forensic AI assistant.

## Available Models

| Model | Base Model | Size | Best For |
|-------|------------|------|----------|
| `eru-llama` | llama3.2:3b | 2GB | Fast responses, low resource usage |
| `eru-llama-large` | llama3.1:8b | 4.7GB | Complex analysis, better reasoning |
| `eru-mistral` | mistral:7b | 4.1GB | Balanced performance |
| `eru-qwen` | qwen2.5:7b | 4.4GB | Strong reasoning, multilingual |
| `eru-gemma` | gemma2:9b | 5.4GB | Efficient, well-rounded |
| `eru-phi` | phi3.5:3.8b | 2.2GB | Small but capable |
| `eru-deepseek` | deepseek-coder-v2:16b | 8.9GB | Code/script analysis |
| `eru-codellama` | codellama:7b | 3.8GB | Malware script analysis |

## Quick Start

1. Install Ollama: https://ollama.ai

2. Create a model:
   ```bash
   ollama create eru-llama -f src/models/Modelfile.eru-llama
   ```

3. Configure Rivendell to use it:
   ```bash
   export RIVENDELL_MODEL_NAME=eru-llama
   ```

## Creating All Models

```bash
cd /path/to/rivendell

# Lightweight (recommended for most systems)
ollama create eru-llama -f src/models/Modelfile.eru-llama
ollama create eru-phi -f src/models/Modelfile.eru-phi

# Medium (8GB+ VRAM)
ollama create eru-mistral -f src/models/Modelfile.eru-mistral
ollama create eru-qwen -f src/models/Modelfile.eru-qwen
ollama create eru-llama-large -f src/models/Modelfile.eru-llama-large
ollama create eru-codellama -f src/models/Modelfile.eru-codellama

# Large (16GB+ VRAM)
ollama create eru-gemma -f src/models/Modelfile.eru-gemma
ollama create eru-deepseek -f src/models/Modelfile.eru-deepseek
```

## Testing a Model

```bash
ollama run eru-llama "What Windows artifacts show evidence of lateral movement?"
```

## Recommendations

- **Limited resources**: Use `eru-llama` or `eru-phi`
- **General use**: Use `eru-mistral` or `eru-qwen`
- **Complex investigations**: Use `eru-llama-large` or `eru-gemma`
- **Script/malware analysis**: Use `eru-codellama` or `eru-deepseek`
