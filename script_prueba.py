
# =========================================
# Databroom - Automated Data Cleaning and Preparation
# Date: 2025-07-29 15:30:39
# =========================================

# Required installation: pip install databroom
import pandas as pd
from databroom.core.broom import Broom

# Load your dataset using Databroom
broom_instance = Broom.from_csv("your_data_file.csv")
print(f"Original shape: {broom_instance.get_df().shape}")

# Apply cleaning operations
broom_instance = broom_instance.remove_empty_cols(threshold=0.9).standardize_column_names().normalize_values()

# Get the cleaned DataFrame
df_cleaned = broom_instance.pipeline.df

# Display results
print("Data cleaning completed!")
print(f"Original shape: {broom_instance.pipeline.df_original.shape}")
print(f"Final shape: {df_cleaned.shape}")
print(f"Columns removed: {broom_instance.pipeline.df_original.shape[1] - df_cleaned.shape[1]}")
print(f"Rows removed: {broom_instance.pipeline.df_original.shape[0] - df_cleaned.shape[0]}")
print("\nFirst 5 rows of cleaned data:")
print(df_cleaned.head())

# Optionally save the cleaned data
# df_cleaned.to_csv("cleaned_data.csv", index=False)

# =========================================
# End of Databroom script
# =========================================