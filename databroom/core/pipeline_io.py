import json
import numpy as np

def normalize_record(rec):
    def convert(v):
        if isinstance(v, np.generic):  # np.float64, np.int64, etc.
            return v.item()
        if isinstance(v, dict):
            return {k: convert(val) for k, val in v.items()}
        if isinstance(v, (list, tuple)):
            return [convert(val) for val in v]
        return v
    return convert(rec)

def save_pipeline(history = None, path: str = "pipeline.json"):
    """Save the data pipeline from a Broom instance"""
    
    history = [normalize_record(rec) for rec in history]
    
    history = [
    {k: v for k, v in d.items() if k not in {"timestamp", "percent_missing_before", "percent_missing_after", "shape_change"}}
    for d in history
    ]
    
    with open(path, 'w', encoding="utf-8") as f:
        if path.endswith(".json"):
            json.dump(history, f, indent=2)
        else:
            raise ValueError("Unsupported pipeline file format.") 
    
    return True

def load_pipeline(path: str):
    """Load data into a Broom instance"""
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            pipeline = json.load(f)
    except json.JSONDecodeError as e:
        print("Error de formato:", e)
        return None
    return pipeline


if __name__ == "__main__":
    # Example usage
    history = [{'timestamp': '2025-09-18 14:11:01', 'function': 'remove_empty_cols', 'args': [], 'kwargs': {}, 'shape_change': {'before': [4, 3], 'after': [4, 2]}, 'percent_missing_before': 41.66666666666667, 'percent_missing_after': 12.5}, {'timestamp': '2025-09-18 14:11:01', 'function': 'remove_empty_rows', 'args': [], 'kwargs': {'threshold': 0.5}, 'shape_change': {'before': [4, 2], 'after': [4, 2]}, 'percent_missing_before': 12.5, 'percent_missing_after': 12.5}]
    
    save_pipeline(history, "pipeline.json")
    
    loaded_history = load_pipeline("pipeline.json")
    print("Loaded History:")
    print(loaded_history)