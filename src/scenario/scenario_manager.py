import json
import os

SCENARIO_DIR = os.path.join(os.path.dirname(__file__), '../../scenarios')

def get_scenario_path(filename):
    if not filename.endswith('.json'):
        filename += '.json'
    # Store in /scenarios directory
    return os.path.abspath(os.path.join(SCENARIO_DIR, filename))

def save_scenario(filename, city_name, closed_edges, description=""):
    scenario = {
        "city_name": city_name,
        "closed_edges": closed_edges,
        "description": description
    }
    os.makedirs(SCENARIO_DIR, exist_ok=True)
    scenario_path = get_scenario_path(filename)
    with open(scenario_path, "w") as f:
        json.dump(scenario, f, indent=2)
    print(f"Saved scenario to {scenario_path}")

def load_scenario(filename):
    scenario_path = get_scenario_path(filename)
    with open(scenario_path, "r") as f:
        scenario = json.load(f)
    return scenario["city_name"], scenario["closed_edges"], scenario.get("description", "")