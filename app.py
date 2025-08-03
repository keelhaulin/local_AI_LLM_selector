import os
import glob
import subprocess

from flask import Flask, request, render_template, redirect, url_for, flash
from huggingface_hub import HfApi

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
app = Flask(__name__)
# Change this in production, or set FLASK_SECRET env var
app.secret_key = os.environ.get("FLASK_SECRET", "change-me")

# -----------------------------------------------------------------------------
# Helper: Suggestion logic
# -----------------------------------------------------------------------------
def suggest_model(use_case: str,
                  gpu_vram_gb: int,
                  context_window: int,
                  perf_target_tpm: int,
                  wants_flash_attention: bool,
                  wants_kv_cache: bool):
    suggestions = []

    # 1) Base models & alignment by use-case
    uc = use_case.lower()
    if uc in ["chat", "general assistant", "voice"]:
        base_models = ["Qwen2.5", "Mistral", "LLaMA3", "Mixtral"]
        alignments = ["Instruct", "Chat", "DPO"]
    elif uc in ["code", "developer"]:
        base_models = ["CodeLLaMA", "DeepSeekCoder", "Qwen-Code"]
        alignments = ["Code", "Instruct"]
    elif uc in ["rag", "embedding", "search"]:
        base_models = ["BGE", "E5", "MiniLM"]
        alignments = ["Base"]
    elif uc in ["thinking", "long reasoning", "planning"]:
        base_models = ["Qwen3", "Yi", "DeepSeek-VL", "OpenChat"]
        alignments = ["DPO", "Instruct"]
    else:
        base_models = ["Qwen2.5", "Mistral"]
        alignments = ["Instruct"]

    # 2) Quantization options by VRAM
    if gpu_vram_gb >= 80:
        quant_options = ["FP16", "Q8_0"]
    elif gpu_vram_gb >= 40:
        quant_options = ["Q6_K", "Q5_0"]
    else:
        quant_options = ["Q4_K_M", "INT4"]

    # 3) Context window variants
    if context_window >= 65536:
        ctx_variants = ["Long", "Max", "64K"]
    else:
        ctx_variants = ["4K", "16K", "32K"]

    # 4) Modifiers
    modifiers = []
    if wants_flash_attention:
        modifiers.append("FlashAttn")
    if wants_kv_cache:
        modifiers.append("KVCache")

    # 5) Performance note
    if perf_target_tpm >= 6:
        perf_note = "✔️ Performance goal achievable."
    else:
        perf_note = "⚠️ May need to optimize quantization or context length."

    # 6) Build suggestions
    for model in base_models:
        for align in alignments:
            for quant in quant_options:
                for ctx in ctx_variants:
                    label = f"{model}-{align}-{ctx}-{quant}"
                    if modifiers:
                        label += "-" + "-".join(modifiers)
                    suggestions.append(label)

    # Return top 10 suggestions
    return suggestions[:10], perf_note

# -----------------------------------------------------------------------------
# Route: Home page (GET) — show form, list HF & local models
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    # scan local models folder
    local_models = [os.path.basename(p) for p in glob.glob("models/*.gguf")]

    # query HF for top 10 public models
    hf_models = []
    try:
        hf_models = [m.modelId for m in HfApi().list_models(limit=10)]
    except Exception as e:
        flash(f"Could not query Hugging Face: {e}", "warning")

    return render_template(
        "index.html",
        local_models=local_models,
        hf_models=hf_models,
        suggestions=None,
        note=None
    )

# -----------------------------------------------------------------------------
# Route: Handle form submission (POST)
# -----------------------------------------------------------------------------
@app.route("/suggest", methods=["POST"])
def suggest():
    # 1) Handle Ollama Pull & Run action
    if request.form.get("action") == "pull_run":
        model = request.form.get("hf_model")
        try:
            # Pull the model via Ollama
            subprocess.run(["ollama", "pull", model], check=True)
            # Launch it
            subprocess.Popen(["ollama", "run", model])
            flash(f"Pulled & running {model}", "success")
        except subprocess.CalledProcessError as e:
            flash(f"Error with Ollama: {e}", "danger")
        # Redirect back to home
        return redirect(url_for("index"))

    # 2) Otherwise, handle suggestion request
    try:
        use_case = request.form.get("use_case", "")
        vram = int(request.form.get("vram", 0))
        ctx = int(request.form.get("context", 0))
        tpm = int(request.form.get("tpm", 0))
        flash_attn = "flash_attn" in request.form
        kv_cache = "kv_cache" in request.form
    except ValueError:
        flash("Please enter valid numeric values for VRAM, Context, and TPM.", "danger")
        return redirect(url_for("index"))

    suggestions, note = suggest_model(
        use_case, vram, ctx, tpm, flash_attn, kv_cache
    )

    # Re-query HF & local models for the template
    local_models = [os.path.basename(p) for p in glob.glob("models/*.gguf")]
    hf_models = []
    try:
        hf_models = [m.modelId for m in HfApi().list_models(limit=10)]
    except Exception:
        hf_models = []

    return render_template(
        "index.html",
        suggestions=suggestions,
        note=note,
        local_models=local_models,
        hf_models=hf_models
    )

# -----------------------------------------------------------------------------
# Run the app
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Listen on all interfaces, port 8500
    app.run(host="0.0.0.0", port=8500)
