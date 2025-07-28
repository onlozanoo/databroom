# 🧹 Janitor Bot

*A cross‑language DataFrame cleaning assistant with an interactive GUI and one‑click code export for ****Python/pandas**** or ****R/tidyverse***.

---

## 📑 Why another cleaner?

Handling missing values, inconsistent column names, and mismatched data types is a routine part of any data workflow. **Janitor Bot** streamlines these repetitive steps through an intuitive interface and generates reproducible code in the language of your choice.

---

## ✨ Features (Current Status)

| Area           | Capability                                                                                                  | Status |
| -------------- | ----------------------------------------------------------------------------------------------------------- | ------ |
| **GUI**        | Streamlit interface with file upload, live preview, and interactive cleaning operations                     | ✅ **COMPLETED** |
| **Core API**   | Chainable `Janitor()` class (`.remove_empty_cols() → .standardize_column_names() → …`)                      | ✅ **COMPLETED** |
| **Export**     | Generate & download Python scripts that reproduce all cleaning operations                                   | ✅ **COMPLETED** |
| **Reporting**  | One‑page HTML summary (missing values, type casts, outliers flagged)                                        | 📋 **PLANNED** |
| **CLI**        | `janitor-bot clean data.csv --lang py` for headless pipelines                                               | 📋 **PLANNED** |
| **R Export**   | R/tidyverse code generation                                                                                 | 📋 **PLANNED** |

---

## 🧰 Cleaning Operations Library

| Function                                        | Purpose                                                                      |
| ----------------------------------------------- | ---------------------------------------------------------------------------- |
| `remove_empty_cols(threshold)`                  | Drops columns whose proportion of missing values exceeds a threshold.        |
| `remove_empty_rows()`                           | Removes rows with all values missing or zero.                                |
| `standardize_column_names()`                    | Converts column names to `snake_case`, strips accents and whitespace.        |
| `convert_types()`                               | Attempts to cast numeric, boolean, and date strings to appropriate dtypes.   |
| `fix_dates()`                                   | Parses and converts date‑like columns to `datetime` objects.                 |
| `deduplicate(subset=None)`                      | Eliminates duplicate rows, optionally based on a subset of columns.          |
| `normalize_strings()`                           | Trims whitespace, lowercases text, and normalizes Unicode in string columns. |
| `detect_outliers(method="zscore", threshold=3)` | Flags potential outliers using Z‑score or IQR methods.                       |
| `fix_encoding_issues()`                         | Detects and converts common mis‑encodings (e.g., Windows‑1252 to UTF‑8).     |
| `clean_categorical(min_freq=0.01)`              | Groups infrequent categories into an `Other` bucket.                         |
| `auto_detect_dirty_columns()`                   | Generates suggestions for columns that may require additional cleaning.      |

---

## 🏗️ Architecture

```
janitor_bot/
├── core/                # Core cleaning engine
│   ├── history_tracker.py # ✅ CleaningCommand decorator for operation tracking
│   ├── pipeline.py      # ✅ CleaningPipeline for operation coordination  
│   ├── cleaning_ops.py  # ✅ Individual cleaning operations (remove_empty_cols, etc.)
│   ├── janitor.py       # ✅ Main user-friendly API with factory methods
│   └── report.py        # 📋 HTML/Rich reports (planned)
├── generators/          # Code template engines
│   ├── base.py          # ✅ Code generator with Jinja2 templates
│   └── templates/       # ✅ Jinja2 templates for Python/R
│       ├── python_pipeline.py.j2  # ✅ Complete Python script template
│       ├── R_pipeline.R.j2         # 📋 R script template (placeholder)
│       └── macros.j2              # ✅ Reusable template components
├── gui/                 # Streamlit app
│   └── app.py           # ✅ Complete GUI with export functionality
├── cli/                 # Typer‑based command‑line interface (planned)
└── tests/               # Unit & integration tests (planned)
```

---

## 🚀 Quick Start (development mode)

```bash
# 1. Clone
git clone https://github.com/onlozanoo/janitor_bot.git && cd janitor_bot

# 2. Create and activate a virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4a. Launch the GUI (recommended)
streamlit run janitor_bot/gui/app.py

# 4b. OR test programmatic API
python pruebas.py
```

**GUI Instructions**: The web app will open at `http://localhost:8501`. Upload your CSV/Excel/JSON file, perform cleaning operations using the sidebar buttons, view results in real-time, and export Python code from the "Export Code" tab.

### **🎯 What's Working Now**

✅ **Complete GUI Workflow**: Upload → Clean → Preview → Export  
✅ **Code Generation**: Full Python scripts with imports, file loading, and operations  
✅ **Interactive Operations**: Remove empty columns/rows, standardize/normalize names/values  
✅ **Real-time Preview**: See changes immediately in the GUI  
✅ **History Tracking**: All operations logged and reproducible  
✅ **File Support**: CSV, Excel (.xlsx/.xls), and JSON files  

### **Current Working Examples**

#### **Basic Usage with Manual Data**
```python
from janitor_bot.core.janitor import Janitor
import pandas as pd

# Create sample data
data = {'Column Name': [1, 2, None, 4], 'Empty Col': [None, None, None, None], 'Data': [5, 6, 7, 8]}
df = pd.DataFrame(data)

# Use Janitor with method chaining
janitor = Janitor(df)
result = janitor.remove_empty_cols(threshold=0.5).standarize_column_names().normalize_column_names()

# Get results
cleaned_df = result.get_df()
history = result.get_history()
```

#### **File Loading with Factory Methods**
```python
from janitor_bot.core.janitor import Janitor

# Load from CSV file
janitor = Janitor.from_csv('data.csv', encoding='utf-8')

# Or auto-detect file type
janitor = Janitor.from_file('data.xlsx')

# Chain multiple operations
cleaned = janitor.remove_empty_cols().standarize_column_names().normalize_values().standarize_values()

print(cleaned.get_df())
```

#### **Available Cleaning Operations**
- `remove_empty_cols(threshold=0.9)` - Remove columns with high missing values
- `remove_empty_rows()` - Remove completely empty rows
- `standarize_column_names()` - Convert to lowercase, replace spaces with underscores
- `normalize_column_names()` - Remove accents and special characters
- `normalize_values()` - Remove accents from all text values
- `standarize_values(columns=None)` - Lowercase + underscore replacement for values

---


## 🛣️ Roadmap

| Milestone                 | Version | Target Month | Highlights                                                                 |
|--------------------------|---------|---------------|---------------------------------------------------------------------------|
| **MVP**                  | `v0.1`  | —             | Core cleaning operations, Streamlit GUI, Python code export, basic tests |
| **Bilingual Release**    | `v0.4`  | —             | R/tidyverse code generator, language toggle in UI, extended report capabilities |
| **Recipes & Rules**      | `v0.5`  | —             | Save/load cleaning pipelines, column-specific rules, cleaning presets     |
| **Extensibility Light**  | `v0.8`  | —             | User-defined cleaning functions, external Python snippet support          |
| **Data Audits**          | `v1.0`  | —             | Great Expectations integration, basic validation reports                  |
| **Export Mastery**       | `v1.5`  | —             | SQL & PySpark exporters, YAML pipeline export, no infrastructure required |
| **(Optional) Cloud Mode**| `v2.0`  | —             | Multi-user hosting, authentication, job history, full SaaS deployment     |

---

## 📋 Implementation Plan

### **PHASE 1: Foundation (Core Basics)**
1. **HistoryTracker** - ✅ **COMPLETED** - Decorator for automatic operation tracking
2. **CleaningPipeline** - ✅ **COMPLETED** - Operation coordination with history tracking
3. **CleaningOperations** - ✅ **COMPLETED** - 7 functions (remove_empty_cols/rows, standardize/normalize names/values)
4. **Janitor** - ✅ **COMPLETED** - User-friendly chainable API with file loading factory methods

### **PHASE 2: Code Generation**
5. **Base Generator** - ✅ **COMPLETED** - Code generator with Jinja2 templates  
6. **Python Generator** - ✅ **COMPLETED** - Complete Python script generation with imports and file loading
7. **Templates Storage** - ✅ **COMPLETED** - Jinja2 templates with macros and dynamic content

### **PHASE 3: Minimal Viable GUI**
8. **Streamlit App** - ✅ **COMPLETED** - File upload, data preview, interactive cleaning operations
9. **GUI Components** - ✅ **COMPLETED** - Operation buttons with parameter controls and history tracking
10. **State Management** - ✅ **COMPLETED** - Session state management with synchronized history

### **PHASE 4: Integration and Export**
11. **Code Export** - ✅ **COMPLETED** - GUI tab with automatic preview and download of Python scripts
12. **Basic Testing** - 📋 **PENDING** - Tests for core functions
13. **Basic CLI** - 📋 **PENDING** - Simple command for headless usage

### **PHASE 5: Expansion**
14. **More Operations** - Add remaining cleaning functions
15. **R Generator** - Implement R templates
16. **Reports** - Basic HTML reports
17. **Configuration** - pyproject.toml, requirements, etc.

### **🎯 Recommended Order**
Start with **PHASE 1** - A solid core foundation allows everything else to work correctly. Each phase can be tested independently before moving to the next.

**Criterion**: Each step should be functional and testable before proceeding to the next.

---

## 🤝 Contributing

I welcome contributions of all kinds.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🧭 Acknowledgements

Janitor Bot is inspired by the daily need to keep data pipelines reliable and maintainable. Thank you to the open‑source community for providing the tools that make this project possible.