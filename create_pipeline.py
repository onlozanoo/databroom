#!/usr/bin/env python3

from databroom.core.broom import Broom

# Load test data
broom = Broom.from_csv('test_data.csv')

# Apply some cleaning operations
broom.clean_columns()  # Clean column names
broom.clean_rows()     # Clean row data

# Save the pipeline
broom.save_pipeline('test_pipeline.json')

print("Pipeline created and saved to test_pipeline.json")
print(f"Applied {len(broom.get_history())} operations:")
for op in broom.get_history():
    print(f"  - {op['function']}")