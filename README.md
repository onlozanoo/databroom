# 🧹 Janitor Bot

*A cross‑language DataFrame cleaning assistant with an interactive GUI and one‑click code export for ****Python/pandas**** or ****R/tidyverse***.

---

## 📑 Why another cleaner?

Handling missing values, inconsistent column names, and mismatched data types is a routine part of any data workflow. **Janitor Bot** streamlines these repetitive steps through an intuitive interface and generates reproducible code in the language of your choice.

---

## ✨ Features (MVP)

| Area           | Capability                                                                                                  |
| -------------- | ----------------------------------------------------------------------------------------------------------- |
| **GUI**        | Streamlit interface with file upload, live preview, and checkbox‑driven cleaning wizard                     |
| **Core API**   | Chainable `Janitor()` class (`.remove_empty_cols() → .standardize_column_names() → …`)                      |
| **Export**     | Generate & download *either* a Python script **or** an R script that reproduces the selected cleaning steps |
| **Reporting**  | One‑page HTML summary (missing values, type casts, outliers flagged)                                        |
| **CLI**        | `janitor-bot clean data.csv --lang py` for headless pipelines                                               |
| **Tests + CI** | Pytest suite & GitHub Actions on every pull request                                                         |

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
├── core/                # Language‑agnostic cleaning logic
│   ├── cleaning_ops.py  # Individual operations
│   └── report.py        # HTML/Rich reports
├── generators/          # Code template engines
│   ├── python.py        # pandas templates (Jinja2)
│   └── r.py             # tidyverse templates (glue)
├── gui/                 # Streamlit app
├── cli/                 # Typer‑based command‑line interface
└── tests/               # Unit & integration tests
```

---

## 🚀 Quick Start (development mode)

```bash
# 1. Clone
git clone https://github.com/<your‑user>/janitor_bot.git && cd janitor_bot

# 2. Create and activate a virtual environment
python -m venv venv && source venv/bin/activate

# 3. Install dependencies (including development extras)
pip install -e .[dev]

# 4. Launch the GUI
streamlit run janitor_bot/gui/app.py
```

---

## 🛣️ Roadmap

| Milestone             | Version | Target Month | Highlights                                                                      |
| --------------------- | ------- | ------------ | ------------------------------------------------------------------------------- |
| **MVP**               | `v0.1`  | Aug 2025     | Core cleaning operations, Streamlit GUI, Python code export, basic tests        |
| **Bilingual Release** | `v0.2`  | Sep 2025     | R/tidyverse code generator, language toggle in UI, extended report capabilities |
| **Recipes & Presets** | `v0.3`  | Oct 2025     | Save/load cleaning pipelines, column‑specific rules                             |
| **Plugin System**     | `v0.4`  | Dec 2025     | Third‑party cleaning operations, Great Expectations integration                 |
| **Cloud Mode**        | `v1.0`  | Q1 2026      | Multi‑user hosting, authentication, job history, SQL & Spark exporters          |

---

## 📋 Implementation Plan

### **PHASE 1: Foundation (Core Basics)**
1. **CleaningCommand** - Simple structure to register operations
2. **CleaningPipeline** - Command list + basic methods (add, execute)
3. **CleaningOperations** - 2-3 basic functions (remove_empty_cols, standardize_names)
4. **Janitor** - Main class with 2-3 methods using the above

### **PHASE 2: Code Generation**
5. **Base Generator** - Abstract class with common interface
6. **Python Generator** - Basic templates for Phase 1 operations
7. **Templates Storage** - Centralized dictionary of templates

### **PHASE 3: Minimal Viable GUI**
8. **Streamlit App** - File upload + basic preview
9. **GUI Components** - Checkboxes for basic operations
10. **State Management** - Connection between GUI and Janitor

### **PHASE 4: Integration and Export**
11. **Code Export** - Button that generates and downloads scripts
12. **Basic Testing** - Tests for core functions
13. **Basic CLI** - Simple command for headless usage

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

We welcome contributions of all kinds. Please see `CONTRIBUTING.md` for guidelines on setting up the development environment, running tests, and submitting pull requests.

---

## 📄 License

This project is licensed under the MIT License.

---

## 🧭 Acknowledgements

Janitor Bot is inspired by the daily need to keep data pipelines reliable and maintainable. Thank you to the open‑source community for providing the tools that make this project possible.

