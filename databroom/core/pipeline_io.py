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
    
    with open(path, 'w') as f:
        if path.endswith(".json"):
            json.dump(history, f, indent=2)
        else:
            raise ValueError("Unsupported pipeline file format.") 
    
    return True

def load_pipeline(history_tracker = None):
    """Load data into a Broom instance"""
    return


if __name__ == "__main__":
    # Example usage
    history = [
        {
            "function": "remove_empty_cols",
            "args": [],
            "kwargs": {"threshold": 0.9}
        },
        {
            "function": "remove_empty_rows",
            "args": [],
            "kwargs": {}
        }
    ]
    
    save_pipeline(history, "pipeline.json")
    """
    loaded_history = load_pipeline()
    print("Loaded History:")
    print(loaded_history)"""