import json

with open("Contextualized_Bangladesh_Legal_Acts.json", "r", encoding="utf-8") as f:
    data = json.load(f)

active_acts = [act for act in data["acts"] if not act.get("is_repealed", False)]
repealed_acts = [act for act in data["acts"] if act.get("is_repealed", False)]

print(f"Active acts: {len(active_acts)}")
print(f"Repealed (excluded): {len(repealed_acts)}")

# Save filtered dataset
data["acts"] = active_acts
with open("Active_Bangladesh_Legal_Acts.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)