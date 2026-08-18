import json
from pathlib import Path

nb_path = Path(r"d:\AI Hackathon\New data\notebooks\test_crewai.ipynb")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Fix Cell 3
nb["cells"][3]["source"] = [
    "llm = LLM(\n",
    "    model=\"gemini/gemini-3.1-flash-lite\",\n",
    "    api_key=os.getenv(\"GEMINI_API_KEY\"),\n",
    "    temperature=0\n",
    ")\n"
]

# Clear any outputs across all cells in test_crewai.ipynb to ensure no sensitive outputs exist
for cell in nb["cells"]:
    if cell.get("cell_type") == "code":
        cell["outputs"] = []
        cell["execution_count"] = None

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print("test_crewai.ipynb cleaned of hardcoded secret key.")
