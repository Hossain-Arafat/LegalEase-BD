# inspect_json.py
import json

with open("G:/LegalEase-BD/legalease_modal/data/chunks/Acts_english.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Type: {type(data)}")
print(f"Keys: {data.keys() if isinstance(data, dict) else 'List'}")
if isinstance(data, dict):
    for key, value in data.items():
        print(f"  {key}: {type(value)} - Length: {len(value) if hasattr(value, '__len__') else 'N/A'}")