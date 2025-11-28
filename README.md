# FixGoblin - Universal Autonomous Debugging System

## 🎯 Overview

FixGoblin is a **universal autonomous debugging system** that automatically detects, analyzes, and fixes bugs in code across **multiple programming languages**. It supports **Python, C++, Java, JavaScript, and C** with full auto-repair capabilities!

### ✨ Multi-Language Support

| Language | Auto-Repair | Error Types | Status |
|----------|-------------|-------------|--------|
| 🐍 **Python** | ✅ Full | Syntax, Runtime, Logical | Production |
| ⚡ **C++** | ✅ Full | Syntax, Compilation, Semantic | Production |
| ☕ **Java** | ✅ Full | Compilation, Type, Runtime | Production |
| 📜 **JavaScript** | ✅ Full | Syntax, Runtime, Type | Production |
| 🔧 **C** | ✅ Full | Syntax, Compilation | Production |

**Fully offline capable!** No internet connection required for core functionality. 🚀

## 📁 Project Structure

```
FixGoblin/
├── fixgoblin.py              # Main CLI entry point
├── launch_ui.sh              # Web UI launcher script
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore rules
├── README.md                # This file
│
└── Backend/
    ├── core/                # Core debugging modules
    │   ├── autonomous_repair.py
    │   ├── universal_repair.py
    │   ├── syntax_fixer.py
    │   ├── error_parser.py
    │   ├── patch_generator.py
    │   ├── patch_optimizer.py
    │   ├── logical_analyzer.py
    │   ├── semantic_detector.py
    │   ├── sandbox_runner.py
    │   ├── multi_language_sandbox.py
    │   ├── cpp_patch_generator.py
    │   ├── java_patch_generator.py
    │   └── js_patch_generator.py
    │
    ├── dsl/                 # DSL parser and rules
    │   ├── fixgoblin_dsl.py
    │   └── *.dsl files
    │
    ├── ui/                  # Web interface
    │   ├── streamlit_app.py
    │   ├── launch_streamlit.sh
    │   └── requirements_streamlit.txt
    │
    └── docs/                # Documentation
        ├── guides/          # User guides
        └── *.md files       # Technical docs
```

## 🚀 Quick Start

### Command Line Usage

#### Python Code
```bash
python fixgoblin.py your_code.py
```

#### C++ Code
```bash
python fixgoblin.py buggy_code.cpp --max-iterations 10
```

#### Java Code
```bash
python fixgoblin.py MyClass.java
```

#### JavaScript Code
```bash
python fixgoblin.py app.js
```

#### Universal Repair (Any Language)
```bash
python universal_repair.py <any_file>
```

Note: `universal_repair.py` is now in `Backend/core/`. Use `fixgoblin.py` as the main entry point.

### Web UI (Streamlit)

```bash
# Launch the web interface
./launch_ui.sh

# Or manually:
streamlit run Backend/ui/streamlit_app.py
```

Access at: `http://localhost:8501`

## 🏗️ Architecture

### 5-Step Pipeline

1. **Sandbox Execution** - Safely executes code in isolated environment
2. **Error Analysis** - Parses errors and extracts diagnostic information
3. **Patch Generation** - Creates multiple fix candidates
4. **Patch Optimization** - Tests and scores patches
5. **Autonomous Repair** - Iteratively applies best patches until code works

## 📊 Key Features

### Autonomous Repair
- Iteratively fixes multiple bugs automatically
- Tracks repair progress across iterations
- Safety limits prevent infinite loops
- Creates automatic backups

### Multi-Language Support
- Python, C++, Java, JavaScript, C
- Language-specific error parsing
- Native compiler/interpreter integration
- Semantic analysis for each language

### Smart Patch Scoring
- +100 points for working patches
- +20 points per error reduced
- -50 points per new error introduced
- Rewards minimal code changes

### Safety Features
- Isolated sandbox testing
- Automatic backup creation (`.backup` files)
- Verification after applying patches
- No modification during testing

## 📝 Usage Examples

### Automatic Repair with Logging
```bash
python fixgoblin.py buggy_code.py --log repair_log.json
```

### With Optimization
```bash
python fixgoblin.py code.py --optimize
```

### Custom Iteration Limit
```bash
python fixgoblin.py code.py --max-iterations 10
```

### Quiet Mode (Summary Only)
```bash
python fixgoblin.py code.py --quiet
```

## 🎓 Documentation

- `README.md` - This file
- `QUICK_GUIDE.md` - Quick reference guide (Backend/docs/)
- `UNIVERSAL_REPAIR_GUIDE.md` - Multi-language usage (Backend/docs/guides/)
- `DSL_USER_GUIDE.md` - DSL rules guide (Backend/docs/guides/)
- `STREAMLIT_UI_GUIDE.md` - Web UI documentation (Backend/docs/guides/)
- `Backend/docs/` - Technical documentation

## ⚙️ Installation

### Requirements
- Python 3.7+
- Standard library only (core functionality)
- Optional: Streamlit for web UI

### Setup
```bash
# Clone or download the repository
cd FixGoblin

# Install optional dependencies (for Streamlit UI)
pip install -r requirements.txt

# Run on any code file
python fixgoblin.py your_code.py
```

## 🔧 Offline Usage

FixGoblin works **completely offline**:
- No internet connection required for core functionality
- All analysis and repairs run locally
- Uses standard Python libraries
- Native compiler/interpreter calls only

## 📄 License

See project documentation for license information.

## 🤝 Contributing

This is a production-ready codebase. For modifications, ensure all changes maintain offline capability and core functionality.

---

**Built for autonomous, offline code debugging across multiple languages** 🛠️
