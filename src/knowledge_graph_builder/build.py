#!/usr/bin/env python3
"""
build.py: Generate world_knowledge_graph.yaml from a source book.
"""

import argparse
import os
import sys
from textwrap import shorten

import yaml
from dotenv import load_dotenv
from llama_api_client import LlamaAPIClient

# ────────────────────────────────────────────────────────────────────────────
# Prompt template
# ────────────────────────────────────────────────────────────────────────────
PROMPT_TEMPLATE = """
You are an **ultra-meticulous literary-analysis AI**. Read the supplied text
_exactly as given_ and create **world_knowledge_graph.yaml** with three
exhaustive sections:

1. book_info   – metadata about the work
2. characters  – every character (main + minor) with rich detail
3. storyline   – events, conflicts, timeline, settings

GLOBAL RULES
• Stick strictly to the text – no invention.
• Be exhaustively complete; missing a character causes real harm.
• Depth over brevity: description/details ≥ 3 sentences; major items 10-12.
• Each event must include WHEN, WHERE, WHO (with role) and WHY.
• Collect ≥ 20 sentences of quotes for each character whenever possible.
• Output **pure YAML** – no markdown fences or commentary.
• Keep empty keys if data is missing.

SCHEMA (shape only – not literal):
book_info:
  title: ""
  author: ""
  publication_year: ""
  genre: ""
  themes: []
  tone_and_style: ""
  narrative_point_of_view: ""
  summary: ""
  intended_audience: ""

characters:
  - name: ""
    aliases: []
    description: ""
    roles: []
    traits: []
    skills_or_powers: []
    items: []
    motivations: ""
    arc: ""
    relationships:
      - with: ""
        label: ""
        details: ""
        history: ""
        quotes: ""          # ≥ 20 sentences
    quotes: ""              # hallmark lines

storyline:
  main_events:
    - event: ""
      quotes: ""
      details: ""          # ≥ 3 sentences incl. characters & roles
  timeline: []
  locations: []
  foreshadowing: []
  motifs_symbols: []
  narrative_tension: []

RETURN one complete YAML document – nothing else.

Here is the book text:
{book_text}
"""

# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────
def strip_fences(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
    if text.rstrip().endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()

def load_book(path):
    if not os.path.exists(path):
        sys.exit(f"❌ Book file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_yaml(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        yaml.safe_dump(data, fp, sort_keys=False, allow_unicode=True)

# ────────────────────────────────────────────────────────────────────────────
# Build routine
# ────────────────────────────────────────────────────────────────────────────
def build_graph(book_path, output_path, model, show_only=False):
    load_dotenv()
    client = LlamaAPIClient(api_key=os.environ.get("LLAMA_API_KEY"))

    book_text = load_book(book_path)
    prompt = PROMPT_TEMPLATE.format(book_text=book_text)

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = completion.completion_message.content.text
    yaml_str = strip_fences(raw)

    try:
        graph = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        print("❌ Failed to parse YAML:", e)
        print("\nFirst 600 characters of model output:\n")
        print(shorten(raw, 600, "..."))
        sys.exit(1)

    if show_only:
        print(yaml.safe_dump(graph, sort_keys=False, allow_unicode=True))
    else:
        save_yaml(graph, output_path)
        print(f"✅ Knowledge graph saved to {output_path}")

# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build world_knowledge_graph.yaml")
    parser.add_argument("--book",  default="book_data/harrypotter.txt",  help="Source book text")
    parser.add_argument("--out",   default="knowledge_base/world_knowledge_graph.yaml",
                        help="Destination YAML file")
    parser.add_argument("--model", default="Llama-4-Maverick-17B-128E-Instruct-FP8",
                        help="Model name for the API")
    parser.add_argument("--show",  action="store_true",
                        help="Parse only and print YAML instead of writing file")
    args = parser.parse_args()

    build_graph(args.book, args.out, args.model, show_only=args.show)