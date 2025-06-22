#!/usr/bin/env python3
"""
build.py — generate world_knowledge_graph.yaml from a source book
"""

import os
import sys
import yaml
from dotenv import load_dotenv
from llama_api_client import LlamaAPIClient

# ────────────────────────────────────────────────────────────────────────────
# 1.  Environment & client
# ────────────────────────────────────────────────────────────────────────────
load_dotenv()
client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))

# ────────────────────────────────────────────────────────────────────────────
# 2.  Paths
# ────────────────────────────────────────────────────────────────────────────
book_path   = "book_data/harrypotter.txt"                  # change if needed
output_path = "knowledge_base/world_knowledge_graph.yaml"

# ────────────────────────────────────────────────────────────────────────────
# 3.  Load book
# ────────────────────────────────────────────────────────────────────────────
if not os.path.exists(book_path):
    print(f"❌ Book file not found: {book_path}")
    sys.exit(1)

with open(book_path, "r", encoding="utf-8") as f:
    book_text = f.read()

# ────────────────────────────────────────────────────────────────────────────
# 4.  Compose prompt  (unchanged from your version)
# ────────────────────────────────────────────────────────────────────────────
prompt = f"""
You are an **ultra-meticulous literary-analysis AI**. …                     # <-- your full prompt here
…
Here is the book text:
{book_text}
"""

# ────────────────────────────────────────────────────────────────────────────
# 5.  Call Llama
# ────────────────────────────────────────────────────────────────────────────
completion = client.chat.completions.create(
    model="Llama-4-Maverick-17B-128E-Instruct-FP8",
    messages=[{"role": "user", "content": prompt}],
)
raw_response = completion.completion_message.content.text

# ────────────────────────────────────────────────────────────────────────────
# 6.  Helper: strip ``` fences if present
# ────────────────────────────────────────────────────────────────────────────
def extract_yaml(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]          # drop the opening fence line
    if text.rstrip().endswith("```"):
        text = text.rsplit("```", 1)[0]        # drop the closing fence
    return text.strip()

# ────────────────────────────────────────────────────────────────────────────
# 7.  Parse YAML & save
# ────────────────────────────────────────────────────────────────────────────
try:
    yaml_str = extract_yaml(raw_response)
    knowledge_graph = yaml.safe_load(yaml_str)          # may raise yaml.YAMLError

    # write only if parsing succeeds
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fp:
        yaml.safe_dump(knowledge_graph, fp,
                       sort_keys=False, allow_unicode=True)

    print(f"✅ Knowledge graph saved to {output_path}")

except Exception as e:
    print("❌ Error parsing or writing YAML:", e)
    print("First 600 characters of model output:\n")
    print(raw_response[:600])
    sys.exit(1)
