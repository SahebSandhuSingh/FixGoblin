# 🎨 Streamlit Frontend Integration Guide

## ✅ Integration Status: FULLY CONNECTED

The Streamlit web interface is now **100% integrated** with the FixGoblin backend debugging system.

---

## 🔌 What Was Integrated

### Backend Modules Imported

```python
from core.autonomous_repair import autonomous_repair
from core.dsl_parser import parse_dsl_config, validate_config, is_rule_allowed
from core.sandbox_runner import run_in_sandbox
from core.error_parser import parse_error
from core.logical_validator import validate_logic
```

### Real Functionality (No Mock Data!)

✅ **Autonomous Repair**: Calls real `autonomous_repair()` function  
✅ **DSL Configuration**: Loads actual DSL config files  
✅ **Sandbox Execution**: Runs code in real sandbox environment  
✅ **Error Detection**: Detects real SyntaxError, RuntimeError, LogicalError  
✅ **Patch Generation**: Generates real code patches  
✅ **Diff Generation**: Shows actual before/after differences  
✅ **Output Capture**: Captures real stdout and stderr  

---

## 🚀 How to Run the Streamlit App

### Method 1: Direct Launch

```bash
cd /Users/aditya/Documents/FixGoblin
streamlit run streamlit_app.py
```

### Method 2: With Custom Port

```bash
streamlit run streamlit_app.py --server.port 8080
```

### Method 3: With Auto-Reload

```bash
streamlit run streamlit_app.py --server.runOnSave true
```

---

## 📋 Features Overview

### 1. Code Input Methods

- **File Upload**: Upload `.py` files directly
- **Code Editor**: Type or paste code in the built-in editor
- **Auto-Detection**: Automatically detects which input to use

### 2. Configuration Options

- **Default Mode**: No restrictions (allows all patches)
- **Strict Logical Rules**: Only logical error fixes
- **Conservative Mode**: Standard debugging patches
- **Aggressive Mode**: Minimal restrictions
- **Custom Config**: Load your own `.dsl` file

### 3. Advanced Settings

- **Max Iterations**: Control repair attempts (1-10)
- **Optimize Efficiency**: Enable/disable performance mode

### 4. Real-Time Results

#### Section 1: Execution Output
- Real stdout from code execution
- Real stderr with error messages
- Live capture from sandbox runner

#### Section 2: Detected Errors
- Error type (SyntaxError, RuntimeError, LogicalError)
- Exact line number
- Priority level (HIGH, MEDIUM, LOW)
- Complete error message
- View all issues in expandable section

#### Section 3: Applied Patches
- Real patch IDs from backend
- Patch descriptions
- Confidence scores
- Changes made (line numbers, error types)
- Status for each patch

#### Section 4: Code Diff
- Unified diff format
- Side-by-side comparison
- Line-by-line highlighting
- Before/after views

#### Section 5: Summary Metrics
- Total iterations performed
- Number of patches applied
- Success rate percentage
- Execution time in seconds

---

## 🔧 Technical Architecture

### Data Flow

```
User Input (Streamlit)
    ↓
Temporary File Creation
    ↓
DSL Config Loading (parse_dsl_config)
    ↓
Autonomous Repair (autonomous_repair)
    ↓
Sandbox Execution (run_in_sandbox)
    ↓
Results Display (Streamlit)
```

### File Handling

1. **Upload/Paste**: User provides code
2. **Temp File**: Creates `tempfile.NamedTemporaryFile`
3. **Processing**: Backend reads from temp file
4. **Cleanup**: Automatically removes temp file

### Configuration Loading

```python
# Load from pre-made configs
config_map = {
    "Strict Logical Rules": "strict_logical_rules.dsl",
    "Conservative Mode": "debug_rules.dsl",
    "Aggressive Mode": "debug_rules_minimal.dsl"
}

# Load custom config
if os.path.exists(custom_config):
    config = parse_dsl_config(custom_config)
```

### Result Processing

```python
# Run repair
result = autonomous_repair(
    file_path=temp_file,
    max_iterations=max_iterations,
    optimize_efficiency=optimize_efficiency
)

# Extract data
iterations = result['iterations']
success = result['success']
final_status = result['final_status']
```

---

## 📊 Session State Management

The app uses Streamlit's session state to persist data:

```python
st.session_state.repair_result      # Full repair result
st.session_state.execution_time     # Time taken
st.session_state.original_code      # Original code
st.session_state.final_code         # Fixed code
```

---

## 🎯 User Workflow

### Step-by-Step Usage

1. **Input Code**
   - Upload a `.py` file, OR
   - Type/paste code in editor

2. **Select Configuration**
   - Choose pre-made config from dropdown
   - Or specify custom `.dsl` file path

3. **Adjust Settings**
   - Set max iterations (default: 5)
   - Toggle efficiency mode

4. **Run Debugger**
   - Click "🚀 Run Debugger" button
   - Watch progress bar

5. **Review Results**
   - Check execution output
   - View detected errors
   - Examine applied patches
   - Compare code diff

6. **Take Action**
   - Download fixed code
   - View JSON report
   - Copy code manually
   - Clear results and start over

---

## 🧪 Testing the Integration

### Quick Test

```bash
python3 test_streamlit_integration.py
```

This will:
- Import all backend modules
- Create buggy code
- Load DSL config
- Run autonomous repair
- Execute in sandbox
- Display results

### Expected Output

```
✅ The Streamlit app is FULLY INTEGRATED with the backend!
✅ All modules imported successfully
✅ Real autonomous_repair() called
✅ Real DSL config loaded
✅ Real sandbox execution
✅ Real stdout/stderr captured
```

---

## 🔍 Verification Checklist

Use this to verify integration:

### Backend Imports
- [x] `autonomous_repair` imported
- [x] `parse_dsl_config` imported
- [x] `run_in_sandbox` imported
- [x] `parse_error` imported
- [x] `validate_logic` imported

### Real Function Calls
- [x] `autonomous_repair()` called with real file
- [x] `parse_dsl_config()` loads actual DSL
- [x] `run_in_sandbox()` executes code
- [x] `difflib.unified_diff()` generates diffs

### No Mock Data
- [x] No hardcoded error messages
- [x] No fake stdout/stderr
- [x] No placeholder patches
- [x] No sample diffs

### Dynamic Updates
- [x] Progress bars show real progress
- [x] Spinners during actual execution
- [x] Results update from backend
- [x] Metrics reflect actual values

---

## 🐛 Troubleshooting

### Import Errors

If you see import errors:

```python
# Check sys.path
import sys
print(sys.path)

# Verify Backend directory exists
import os
print(os.path.exists('Backend/core'))
```

### DSL Config Not Found

```python
# Check if config files exist
configs = [
    "strict_logical_rules.dsl",
    "debug_rules.dsl", 
    "debug_rules_minimal.dsl"
]
for c in configs:
    print(f"{c}: {os.path.exists(c)}")
```

### Temp File Issues

```python
# Verify temp directory is writable
import tempfile
temp = tempfile.gettempdir()
print(f"Temp dir: {temp}")
print(f"Writable: {os.access(temp, os.W_OK)}")
```

---

## 📈 Performance Considerations

### File Size Limits

- **Recommended**: Files under 10,000 lines
- **Maximum**: Limited by system memory
- **Large Files**: May take longer to process

### Iteration Limits

- **Default**: 5 iterations
- **Minimum**: 1 iteration
- **Maximum**: 10 iterations
- **Recommended**: 5-7 for most cases

### Memory Usage

- Each iteration stores result in session state
- Clear results to free memory
- Restart app if memory issues occur

---

## 🎨 Customization

### Change Default Config

Edit `streamlit_app.py`:

```python
selected_config = st.selectbox(
    "Debug Configuration:",
    ["Default (No restrictions)",
     "Strict Logical Rules",  # <- Change this
     "Conservative Mode",
     "Aggressive Mode",
     "Custom Config..."],
    index=1  # <- Change default selection
)
```

### Modify Max Iterations

```python
max_iterations = st.slider(
    "Max Iterations:",
    min_value=1,
    max_value=15,  # <- Increase maximum
    value=5,       # <- Change default
    step=1
)
```

### Add New Config Preset

```python
config_map = {
    "Strict Logical Rules": "strict_logical_rules.dsl",
    "Conservative Mode": "debug_rules.dsl",
    "Aggressive Mode": "debug_rules_minimal.dsl",
    "My Custom Mode": "my_config.dsl"  # <- Add new
}
```

---

## 📚 Related Documentation

- **Backend Architecture**: `Backend/docs/ARCHITECTURE.md`
- **DSL Parser Guide**: `Backend/docs/DSL_PARSER_GUIDE.md`
- **Quick Reference**: `Backend/docs/QUICK_REFERENCE.md`
- **System Flow**: `Backend/docs/SYSTEM_FLOW.md`
- **Quickstart**: `QUICKSTART_DSL.md`

---

## 🎉 Summary

### What Changed from Mock Version

| Feature | Mock Version | Integrated Version |
|---------|--------------|-------------------|
| Imports | None | All backend modules |
| Code Execution | Fake | Real sandbox runner |
| Error Detection | Hardcoded | Real error parser |
| Patches | Sample | Real patch generator |
| Diffs | Static | Dynamic from difflib |
| Stdout/Stderr | Placeholder | Real output capture |
| Configuration | Unused | Real DSL loading |

### Key Advantages

✅ **Real-Time Debugging**: Actual code execution  
✅ **Production Ready**: No mock/placeholder data  
✅ **Fully Featured**: All backend capabilities  
✅ **User Friendly**: Simple web interface  
✅ **Configurable**: DSL-based customization  
✅ **Transparent**: Shows all repair steps  

---

**🚀 The Streamlit app is now a fully functional, production-ready web interface for FixGoblin!**
