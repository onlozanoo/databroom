# 🧹 Databroom

*A powerful DataFrame cleaning tool with **Command Line Interface**, **Interactive GUI**, and **Programmatic API** - automatically generates reproducible **Python/pandas**, **R/tidyverse** code, and **CLI** Commands*

[![PyPI version](https://badge.fury.io/py/databroom.svg)](https://pypi.org/project/databroom/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)


<p align='center'>
<img width="612" height="612" alt="Image" src="https://github.com/user-attachments/assets/33b7c8fe-4aee-4459-ab68-61ff4004ac98" />
</p>

## 📑 Table of Contents

- [🧹 Databroom](#-databroom)
  - [📑 Table of Contents](#-table-of-contents)
  - [🆚 Why Databroom?](#-why-databroom)
    - [**The Problem: Manual Data Cleaning is Tedious**](#the-problem-manual-data-cleaning-is-tedious)
    - [**The Benefits**](#the-benefits)
    - [**Real-world Comparison**](#real-world-comparison)
    - [**When to Use Databroom**](#when-to-use-databroom)
  - [🚀 Quick Start](#-quick-start)
    - [Installation](#installation)
    - [Command Line Interface (Primary Interface)](#command-line-interface-primary-interface)
    - [Interactive GUI](#interactive-gui)
    - [GUI Screenshots](#gui-screenshots)
    - [Programmatic API](#programmatic-api)
  - [✨ Features](#-features)
    - [**🖥️ Command Line Interface**](#️-command-line-interface)
    - [**🎨 Interactive GUI**](#-interactive-gui)
    - [**⚙️ Programmatic API**](#️-programmatic-api)
    - [**🔄 Code Generation**](#-code-generation)
  - [🧰 Available Cleaning Operations](#-available-cleaning-operations)
    - [CLI Parameters](#cli-parameters)
  - [📊 Example Workflows](#-example-workflows)
    - [**Data Science Pipeline**](#data-science-pipeline)
    - [**R/Tidyverse Workflow**](#rtidyverse-workflow)
    - [**Batch Processing Setup**](#batch-processing-setup)
  - [🏗️ Architecture](#️-architecture)
  - [🛠️ Development](#️-development)
    - [Local Development](#local-development)
    - [Testing](#testing)
    - [Code Quality](#code-quality)
  - [📈 Project Status](#-project-status)
  - [🤝 Contributing](#-contributing)
    - [**Ways to Contribute**](#ways-to-contribute)
  - [📄 License](#-license)

---

## 🆚 Why Databroom? 

### **The Problem: Manual Data Cleaning is Tedious**

**With pandas (manual approach):**
```python
import pandas as pd
import unicodedata

# Read the file
df = pd.read_csv("messy_data.csv")

# Remove columns with more than 90% missing values
threshold = 0.9
df = df.loc[:, df.isnull().mean() < threshold]

# Standardize column names manually
df.columns = df.columns.str.lower().str.replace(' ', '_')

# Normalize text values (removing accents)
def normalize_text(text):
    if not isinstance(text, str):
        return text
    return ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )

# Apply to all string columns (need to identify them first)
string_cols = df.select_dtypes(include=['object']).columns
for col in string_cols:
    df[col] = df[col].apply(normalize_text)

# Save the result
df.to_csv("clean_data.csv", index=False)
```

**With Databroom (one command):**
```bash
databroom clean messy_data.csv \
  --clean-all \
  --output-file clean_data.csv \
  --output-code cleaning_script.py
```

### **The Benefits**

| Feature | Manual Pandas | Databroom |
|---------|---------------|-----------|
| **Lines of code** | ~20+ lines | 1 command |
| **Time to implement** | 10-15 minutes | 10 seconds |
| **Error prone** | High (manual logic) | Low (tested operations) |
| **Reproducible** | Need to save script | Auto-generates code |
| **Cross-language** | Python only | Python + R output |
| **GUI option** | No | Yes (`databroom gui`) |
| **Parameter tuning** | Manual coding | CLI flags & GUI sliders |

### **Real-world Comparison**

**Complex cleaning task:**
```python
# Pandas approach: ~50 lines of code
import pandas as pd
import unicodedata
import numpy as np

df = pd.read_excel("survey_data.xlsx")

# Remove empty columns
empty_threshold = 0.8
df = df.dropna(axis=1, thresh=int(empty_threshold * len(df)))

# Remove empty rows  
df = df.dropna(how='all')

# Fix column names
df.columns = df.columns.str.lower()
df.columns = df.columns.str.replace(' ', '_')
df.columns = df.columns.str.replace('[^a-z0-9_]', '', regex=True)

# Normalize text in all string columns
def clean_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return text
    # Remove accents
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return text

string_columns = df.select_dtypes(include=['object']).columns
for col in string_columns:
    df[col] = df[col].apply(clean_text)

df.to_csv("cleaned_survey.csv", index=False)
```

**Databroom approach:**
```bash
databroom clean survey_data.xlsx \
  --clean-all \
  --empty-threshold 0.8 \
  --output-file cleaned_survey.csv \
  --output-code survey_cleaning.py \
  --verbose
```

**Result:** Same output, 1 command, includes reproducible script generation.

### **When to Use Databroom**

✅ **Perfect for:**
- **🤖 Full automation** - Transform your entire data cleaning pipeline into a single command
- Quick data exploration and cleaning
- Batch processing multiple files
- Learning data cleaning best practices
- Generating reproducible cleaning scripts
- Teams needing consistent data preprocessing
- Converting workflows between Python and R

---

## 🚀 Quick Start

### Installation

```bash
# Complete installation - CLI + GUI + API (recommended)
pip install databroom

# Verify installation
databroom --version

# CLI + API only (no Streamlit GUI)
pip install databroom[cli]

# GUI + API only (no CLI interface)  
pip install databroom[gui]
```

### Command Line Interface (Primary Interface)

Clean your data files instantly with powerful CLI commands:

```bash
# Smart clean everything (recommended)
databroom clean data.csv --clean-all --output-file clean.csv

# Column cleaning with custom threshold
databroom clean messy.xlsx --clean-columns --empty-threshold 0.8 --output-file cleaned.xlsx

# Complete cleaning pipeline with code generation
databroom clean survey.csv --clean-all --output-code cleaning_script.py --lang python

# Generate R/tidyverse code
databroom clean data.csv --clean-rows --output-code analysis.R --lang r

# Advanced options with verbose output
databroom clean dataset.json --clean-all --no-snakecase --verbose --info

# Launch interactive GUI
databroom gui

# List all available operations
databroom list
```

### Interactive GUI

Launch the web-based interface for visual data cleaning:

```bash
databroom gui
# Opens http://localhost:8501 in your browser
```

<!-- GUI SCREENSHOTS SECTION - PLACEHOLDER -->
### GUI Screenshots

*[GUI screenshots will be added here to showcase the interactive interface, file upload, operation panels, live preview, and code generation features]*

<!-- END GUI SCREENSHOTS SECTION -->

### Programmatic API

Use Databroom directly in your Python scripts:

```python
from databroom.core.broom import Broom

# Load and clean data with method chaining
broom = Broom.from_csv('data.csv')
result = broom.clean_all()  # Smart clean everything

# Or use specific operations
result = (broom
    .clean_columns(empty_threshold=0.9)
    .clean_rows())

# Get cleaned DataFrame
cleaned_df = result.get_df()
print(f"Cleaned {cleaned_df.shape[0]} rows × {cleaned_df.shape[1]} columns")

# Generate reproducible code
from databroom.generators.base import CodeGenerator
generator = CodeGenerator('python')
generator.load_history(result.get_history())
generator.export_code('my_cleaning_pipeline.py')
```

---

## ✨ Features

### **🖥️ Command Line Interface**
- **Instant cleaning** with intuitive flags and parameters
- **Batch processing** capabilities for multiple files
- **Code generation** in Python/pandas and R/tidyverse
- **Flexible output** formats (CSV, Excel, JSON)
- **Rich help** system with examples and colored output
- **Verbose mode** for detailed operation feedback

### **🎨 Interactive GUI**
- **Drag & drop** file upload (CSV, Excel, JSON)
- **Live preview** of cleaning operations
- **Interactive parameter tuning** with sliders and inputs
- **Real-time code generation** with syntax highlighting
- **One-click download** of cleaned data and generated scripts
- **Operation history** with undo functionality

### **⚙️ Programmatic API**
- **Chainable methods** for fluent data cleaning workflows
- **Factory methods** for easy file loading (`from_csv()`, `from_excel()`, etc.)
- **History tracking** for reproducible operations
- **Template-based code generation** with Jinja2

### **🔄 Code Generation**
- **Complete scripts** with imports, file loading, and execution
- **Cross-language support** (Python/pandas ↔ R/tidyverse)
- **Template system** for customizable output formats
- **Reproducible workflows** that can be shared and version controlled

---

## 🧰 Available Cleaning Operations

| Operation | CLI Flag | Purpose |
|-----------|----------|---------|
| **🧹 Clean All** | `--clean-all` | **Smart clean everything: columns + rows with all operations** |
| **📌 Promote Headers** | `--promote-headers` | **Convert a data row to column headers** |
| **📋 Clean Columns** | `--clean-columns` | Clean column names: snake_case + remove accents + remove empty |
| **📊 Clean Rows** | `--clean-rows` | Clean row data: snake_case + remove accents + remove empty |

### CLI Parameters

```bash
# Smart Operations (recommended)
--clean-all                          # Clean everything: columns + rows
--clean-columns                      # Clean column names only
--clean-rows                         # Clean row data only

# Structure Operations
--promote-headers                    # Convert data row to column headers
--promote-row-index 1                # Row index to promote (default: 0)
--keep-promoted-row                  # Keep the promoted row in data

# Advanced Options (disable specific operations)
--no-snakecase                       # Keep original text case in rows
--no-snakecase-cols                  # Keep original column name case
--no-remove-accents-vals             # Keep accents in text values
--no-remove-empty-cols               # Keep empty columns

# Parameters
--empty-threshold 0.8                # Custom missing value threshold (default: 0.9)

# Output options
--output-file cleaned.csv            # Save cleaned data
--output-code script.py              # Generate code file
--lang python                        # Code language (python/r)

# Behavior options
--verbose                            # Detailed output
--quiet                              # Minimal output  
--info                               # Show DataFrame info
```

---

## 📊 Example Workflows

### **Data Science Pipeline**
```bash
# Clean survey data and generate analysis script
databroom clean survey_data.xlsx \
  --clean-all \
  --empty-threshold 0.7 \
  --output-file clean_survey.csv \
  --output-code survey_analysis.py \
  --verbose
```

### **R/Tidyverse Workflow**
```bash
# Generate R script for tidyverse users
databroom clean research_data.csv \
  --clean-all \
  --output-code tidyverse_pipeline.R \
  --lang r
```

### **Batch Processing Setup**
```bash
# Process multiple files with consistent operations
for file in data/*.csv; do
  databroom clean "$file" \
    --clean-columns \
    --output-file "clean_$(basename "$file")" \
    --quiet
done
```

---

## 🏗️ Architecture

Databroom follows a modular architecture designed for extensibility and maintainability:

```
databroom/
├── cli/                 # Command line interface (Typer + Rich)
│   ├── main.py          # Entry point and app configuration
│   ├── commands.py      # CLI commands (clean, gui, list)
│   ├── operations.py    # Operation parsing and execution
│   └── utils.py         # File handling and code generation
├── core/                # Core cleaning engine
│   ├── broom.py         # Main API with method chaining
│   ├── pipeline.py      # Operation coordination and state management  
│   ├── cleaning_ops.py  # Individual cleaning operations
│   └── history_tracker.py # Automatic operation tracking
├── generators/          # Code generation system
│   ├── base.py          # Template-based code generator
│   └── templates/       # Jinja2 templates for Python/R
├── gui/                 # Modular Streamlit web interface
│   ├── app.py           # Main orchestrator (83 lines)
│   ├── components/      # Reusable UI components
│   │   ├── file_upload.py    # File upload and processing
│   │   ├── operations.py     # Data cleaning operations
│   │   ├── controls.py       # Step back, reset, reload controls
│   │   └── tabs.py          # Data display and export tabs
│   └── utils/           # GUI utilities
│       ├── session.py        # Session state management
│       └── styles.py         # CSS styling and theming
└── tests/               # Comprehensive test suite
```

---

## 🛠️ Development

### Local Development

```bash
# Clone repository
git clone https://github.com/onlozanoo/databroom.git
cd databroom

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev,cli,all]"

# Run tests
pytest

# Run CLI locally
python -m databroom.cli.main --help
```

### Testing

```bash
# Run full test suite
pytest

# Run with coverage
pytest --cov=databroom

# Run specific test categories
pytest -m "not slow"           # Skip slow tests
pytest tests/cli/              # Test CLI only
pytest tests/core/             # Test core functionality
```

### Code Quality

```bash
# Format code
black databroom/
isort databroom/

# Lint
flake8 databroom/

# Type check
mypy databroom/
```

---

## 📈 Project Status

**Current Version**: v0.3.1 - **Production Ready & Live on PyPI**

✅ **Fully Implemented**
- **Smart Operations**: `--clean-all`, `--clean-columns`, `--clean-rows`, `--promote-headers`
- **Modular GUI Architecture**: Organized components with 86% code reduction
- Complete CLI with simplified and legacy operations
- Interactive Streamlit GUI with live preview and organized operations
- Programmatic API with method chaining
- Python and R code generation with parameter filtering
- Comprehensive test suite
- **Live on PyPI**: `pip install databroom`
- Dynamic new operations loading system
- Extensible component-based GUI structure

🚧 **In Active Development**  
- Extended cleaning operations library
- Advanced parameter validation
- Performance optimizations
- Enhanced error handling

📋 **Planned Features**
- Preview in CLI
- Configuration presets and templates
- Enhanced batch processing workflows
- Save/load cleaning pipelines as JSON
- Custom cleaning operation plugins system
- Integration with pandas-profiling and data validation tools
- Advanced data quality reporting and metrics

---

## 🤝 Contributing

I welcome contributions! Here's how you can help:

### **Ways to Contribute**
- 🐛 **Bug Reports**: Submit issues with detailed reproduction steps
- 💡 **Feature Requests**: Propose new cleaning operations or CLI features
- 📝 **Documentation**: Improve examples, tutorials, or API docs
- 🧪 **Testing**: Add test cases or improve test coverage
- 💻 **Code**: Implement new features or fix existing issues

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/databroom/
- **GitHub Repository**: https://github.com/onlozanoo/databroom
- **Documentation**: This README
- **Issues & Support**: https://github.com/onlozanoo/databroom/issues

*Built with ❤️ for the data science community*
