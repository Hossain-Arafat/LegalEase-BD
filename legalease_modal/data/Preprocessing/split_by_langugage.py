# preprocessing/split_by_language.py
import json

with open("Active_Bangladesh_Legal_Acts.json", "r") as f:
    data = json.load(f)

english_acts = []
bengali_acts = []
unknown_acts = []

for act in data["acts"]:
    lang = act.get("language", "").lower().strip()
    title = act.get("act_title", "")
    
    # Detect by language field first, then by title script
    if lang in ["en", "english"]:
        english_acts.append(act)
    elif lang in ["bn", "bengali", "bangla"]:
        bengali_acts.append(act)
    else:
        # Detect Bengali script by Unicode range
        bengali_chars = sum(1 for c in title if '\u0980' <= c <= '\u09FF')
        if bengali_chars > 3:
            bengali_acts.append(act)
        else:
            english_acts.append(act)

print(f"English acts : {len(english_acts)}")
print(f"Bengali acts : {len(bengali_acts)}")
print(f"Unknown acts : {len(unknown_acts)}")

# Save separately
for name, acts in [("english", english_acts), ("bengali", bengali_acts)]:
    out = {**data, "acts": acts}
    with open(f"Acts_{name}.json", "w", ensure_ascii=False) as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Saved Acts_{name}.json with {len(acts)} acts")