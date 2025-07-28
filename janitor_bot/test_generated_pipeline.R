
# =========================================
# Janitor Bot - Automated Data Cleaning and Preparation
# Date: 2025-07-28 11:38:30
# =========================================

# Required packages: tidyverse, janitor, stringi
# Install with: install.packages(c("tidyverse", "janitor", "stringi"))

library(tidyverse)
library(janitor)
library(stringi)

# Load your dataset
df_original <- read_csv("your_data_file.csv", show_col_types = FALSE)
cat("Original shape:", nrow(df_original), "rows x", ncol(df_original), "columns\n")

# Apply cleaning operations using tidyverse pipe syntax
df_cleaned <- df_original %>%
  select_if(~ mean(is.na(.)) < 0.09999999999999998) %>%
  clean_names(case = 'snake') %>%
  rename_with(~ stri_trans_general(., 'Latin-ASCII')) %>%
  mutate(across(where(is.character), ~ str_to_lower(str_replace_all(., ' ', '_'))))

# Display results
cat("\nData cleaning completed!\n")
cat("Original shape:", nrow(df_original), "rows x", ncol(df_original), "columns\n")
cat("Final shape:", nrow(df_cleaned), "rows x", ncol(df_cleaned), "columns\n")
cat("Columns removed:", ncol(df_original) - ncol(df_cleaned), "\n")
cat("Rows removed:", nrow(df_original) - nrow(df_cleaned), "\n")

cat("\nFirst 5 rows of cleaned data:\n")
print(head(df_cleaned))

# Column summary
cat("\nColumn summary:\n")
glimpse(df_cleaned)

# Optionally save the cleaned data
# write_csv(df_cleaned, "cleaned_data.csv")

# =========================================
# End of Janitor Bot script
# =========================================