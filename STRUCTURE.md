# FixGoblin Project Structure

## Root Directory (Production Files Only)
```
FixGoblin/
├── fixgoblin.py          # Main CLI entry point
├── launch_ui.sh          # Web UI launcher
├── requirements.txt      # Dependencies
├── .gitignore           # Git configuration
├── README.md            # Main documentation
└── Backend/             # All implementation files
```

## Backend Organization

### Backend/core/
Core debugging and repair modules:
- `autonomous_repair.py` - Iterative auto-repair engine
- `universal_repair.py` - Multi-language repair orchestrator
- `syntax_fixer.py` - Syntax error handler
- `error_parser.py` - Error extraction and parsing
- `patch_generator.py` - Fix candidate generation
- `patch_optimizer.py` - Patch testing and scoring
- `logical_analyzer.py` - Logical error detection
- `logical_validator.py` - Logic validation
- `semantic_detector.py` - Semantic analysis
- `sandbox_runner.py` - Safe code execution
- `multi_language_sandbox.py` - Multi-language sandbox
- `test_case_validator.py` - Test validation
- `final_report.py` - Report generation
- `cpp_patch_generator.py` - C++ patch generation
- `java_patch_generator.py` - Java patch generation
- `js_patch_generator.py` - JavaScript patch generation
- `dsl_parser.py` - DSL parsing engine

### Backend/dsl/
DSL-related files:
- `fixgoblin_dsl.py` - DSL parser implementation
- `debug_rules.dsl` - Debug rule definitions
- `debug_rules_minimal.dsl` - Minimal rule set
- `strict_logical_rules.dsl` - Strict logical rules

### Backend/ui/
Web interface files:
- `streamlit_app.py` - Streamlit web application
- `launch_streamlit.sh` - Streamlit launcher
- `requirements_streamlit.txt` - UI dependencies

### Backend/docs/
Documentation:
- `ARCHITECTURE.md` - System architecture
- `DSL_PARSER_GUIDE.md` - DSL parser documentation
- `FINAL_REPORT.md` - Report format documentation
- `QUICKSTART.md` - Quick start guide
- `QUICK_REFERENCE.md` - API reference
- `QUICK_GUIDE.md` - Quick guide
- `NO_RESTRICTIONS.md` - Usage guidelines
- `NO_SURPRISES_GUARANTEE.md` - Behavior guarantees
- `QUICK_REFERENCE_MULTILANG.py` - Multi-language examples

### Backend/docs/guides/
User guides:
- `DSL_USER_GUIDE.md` - DSL usage guide
- `HOW_TO_USE_DSL.md` - DSL tutorial
- `QUICKSTART_DSL.md` - DSL quick start
- `LOGICAL_ANALYZER_GUIDE.md` - Logical analysis guide
- `MULTI_LANGUAGE_GUIDE.md` - Multi-language support guide
- `UNIVERSAL_REPAIR_GUIDE.md` - Universal repair guide
- `STREAMLIT_INTEGRATION_GUIDE.md` - Streamlit integration
- `STREAMLIT_README.md` - Streamlit documentation
- `STREAMLIT_UI_GUIDE.md` - UI usage guide

## Key Features
- ✅ Clean root directory with only essential entry points
- ✅ Organized backend structure by functionality
- ✅ All documentation in Backend/docs/
- ✅ Separate UI, DSL, and core modules
- ✅ Production-ready, fully offline capable
- ✅ No test files, no clutter

## Usage
```bash
# CLI usage
python fixgoblin.py your_code.py

# Web UI
./launch_ui.sh
```
