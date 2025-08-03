
from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<title>LLM Model Selector</title>
<h1>🧠 LLM Model Selector for Local Inference</h1>
<form method="post">
    Use Case (chat, code, rag, thinking): <input name="use_case"><br><br>
    GPU VRAM (GB): <input name="vram" type="number"><br><br>
    Context Window: <input name="context" type="number"><br><br>
    Min Tokens per Minute: <input name="tpm" type="number"><br><br>
    <input type="checkbox" name="flash_attn"> Flash Attention<br>
    <input type="checkbox" name="kv_cache"> KV Cache<br><br>
    <input type="submit" value="Suggest Models">
</form>

{% if suggestions %}
    <h3>🔍 Suggested Models:</h3>
    <ul>
    {% for s in suggestions %}
        <li>{{ s }}</li>
    {% endfor %}
    </ul>
    <p><strong>{{ note }}</strong></p>
{% endif %}
'''

def suggest_model(use_case, gpu_vram_gb, context_window, perf_target_tpm, wants_flash_attention, wants_kv_cache):
    suggestions = []

    if use_case.lower() in ["chat", "general assistant", "voice"]:
        base_models = ["Qwen2.5", "Mistral", "LLaMA3", "Mixtral"]
        alignments = ["Instruct", "Chat", "DPO"]
    elif use_case.lower() in ["code", "developer"]:
        base_models = ["CodeLLaMA", "DeepSeekCoder", "Qwen-Code"]
        alignments = ["Code", "Instruct"]
    elif use_case.lower() in ["rag", "embedding", "search"]:
        base_models = ["BGE", "E5", "MiniLM"]
        alignments = ["Base"]
    elif use_case.lower() in ["thinking", "long reasoning", "planning"]:
        base_models = ["Qwen3", "Yi", "DeepSeek-VL", "OpenChat"]
        alignments = ["DPO", "Instruct"]
    else:
        base_models = ["Qwen2.5", "Mistral"]
        alignments = ["Instruct"]

    if gpu_vram_gb >= 80:
        quant_options = ["FP16", "Q8_0"]
    elif gpu_vram_gb >= 40:
        quant_options = ["Q6_K", "Q5_0"]
    else:
        quant_options = ["Q4_K_M", "INT4"]

    if context_window >= 65536:
        long_context_variants = ["Long", "Max", "64K"]
    else:
        long_context_variants = ["4K", "16K", "32K"]

    modifiers = []
    if wants_flash_attention:
        modifiers.append("FlashAttn")
    if wants_kv_cache:
        modifiers.append("KVCache")

    if perf_target_tpm >= 6:
        perf_note = "✔️ Performance goal achievable."
    else:
        perf_note = "⚠️ May need to optimize quantization or context length."

    for model in base_models:
        for align in alignments:
            for quant in quant_options:
                for ctx in long_context_variants:
                    label = f"{model}-{align}-{ctx}-{quant}"
                    if modifiers:
                        label += "-" + "-".join(modifiers)
                    suggestions.append(label)

    return suggestions[:10], perf_note

@app.route("/", methods=["GET", "POST"])
def index():
    suggestions, note = None, None
    if request.method == "POST":
        use_case = request.form.get("use_case", "")
        try:
            vram = int(request.form.get("vram", 0))
            context = int(request.form.get("context", 0))
            tpm = int(request.form.get("tpm", 0))
        except ValueError:
            return render_template_string(TEMPLATE, suggestions=None, note="Invalid input.")
        flash_attn = 'flash_attn' in request.form
        kv_cache = 'kv_cache' in request.form
        suggestions, note = suggest_model(use_case, vram, context, tpm, flash_attn, kv_cache)

    return render_template_string(TEMPLATE, suggestions=suggestions, note=note)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8500)
