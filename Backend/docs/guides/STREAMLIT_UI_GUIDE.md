# 🎨 FixGoblin Streamlit Web Interface

**A modern, fully-integrated web UI for autonomous Python code debugging**

---

## ⚡ Quick Start

### Launch the App

```bash
# Option 1: Using the launch script
./launch_streamlit.sh

# Option 2: Direct command
streamlit run streamlit_app.py
```

The app will open automatically at `http://localhost:8501`

---

## 📦 Prerequisites

Ensure you have:

- ✅ Python 3.8 or higher
- ✅ Streamlit (`pip install streamlit`)
- ✅ All backend dependencies installed

```bash
# Install Streamlit
pip3 install streamlit

# Verify installation
streamlit --version
```

---

## 🎯 Features

### 1. Code Input
- **📁 File Upload**: Drag & drop `.py` files
- **✏️ Code Editor**: Built-in text editor with syntax highlighting
- **🔄 Auto-Detection**: Automatically uses uploaded file or typed code

### 2. Configuration
- **Default Mode**: No restrictions
- **Strict Logical Rules**: Only logical error fixes
- **Conservative Mode**: Standard debugging
- **Aggressive Mode**: Minimal restrictions
- **Custom Config**: Load your own `.dsl` file

### 3. Advanced Settings
- **Max Iterations**: 1-10 repair attempts
- **Optimize Efficiency**: Performance mode toggle

### 4. Real-Time Results

#### 📤 Execution Output
- Live stdout capture
- Live stderr capture
- Sandbox execution results

#### 🐛 Detected Errors
- Error type (SyntaxError, RuntimeError, LogicalError)
- Line numbers
- Priority levels
- Detailed error messages
- View all issues

#### 🔧 Applied Patches
- Patch IDs from backend
- Descriptions of fixes
- Confidence scores
- Change summaries

#### 📊 Code Diff
- Unified diff view
- Side-by-side comparison
- Line-by-line highlighting

#### 📋 Summary
- Iterations count
- Patches applied
- Success rate
- Execution time

---

## 🔌 Backend Integration

### Fully Connected Modules

```python
✅ autonomous_repair    # Core repair engine
✅ dsl_parser          # Configuration loader
✅ sandbox_runner      # Code execution
✅ error_parser        # Error detection
✅ logical_validator   # Logic checking
```

### No Mock Data
- ✅ Real code execution
- ✅ Real error detection
- ✅ Real patch generation
- ✅ Real DSL configuration
- ✅ Real stdout/stderr

---

## 📖 Usage Guide

### Step 1: Input Your Code

**Option A: Upload File**
1. Click "Browse files" button
2. Select a `.py` file
3. File content appears in editor

**Option B: Type/Paste Code**
1. Click in the code editor
2. Type or paste your code
3. Code is ready for debugging

### Step 2: Choose Configuration

**Pre-made Configs:**
- **Default**: Allows all patches
- **Strict Logical**: Only logical fixes
- **Conservative**: Standard debugging
- **Aggressive**: Minimal restrictions

**Custom Config:**
1. Select "Custom Config..." from dropdown
2. Enter path to your `.dsl` file
3. Example: `my_debug_rules.dsl`

### Step 3: Adjust Settings

**Max Iterations**
- How many repair attempts to make
- Recommended: 5-7 iterations
- Range: 1-10

**Optimize Efficiency**
- Enable for faster execution
- Uses efficiency mode in backend

### Step 4: Run Debugger

1. Click **"🚀 Run Debugger"** button
2. Watch the progress bar
3. Wait for results

### Step 5: Review Results

**Execution Output**
- Check stdout for program output
- Check stderr for error messages

**Detected Errors**
- View error type and line number
- Read error messages
- Expand to see all issues

**Applied Patches**
- See which patches were applied
- Review patch descriptions
- Check confidence scores

**Code Diff**
- Compare original vs fixed code
- See exact changes made
- Review side-by-side

### Step 6: Take Action

**Download Fixed Code**
- Click "💾 Download Fixed Code"
- Save as `.py` file
- Use in your project

**View Fixed Code**
- Click "📋 View Fixed Code"
- Copy manually from text area

**View JSON Report**
- Click "📄 View JSON Report"
- See complete repair history
- Export for documentation

**Clear Results**
- Click "🔄 Clear Results"
- Reset for new debugging session

---

## 🔍 Example Session

### Input Code (Buggy)
```python
def calculate_discount(price, percent):
    '''Calculate final price after discount'''
    discount = price * percent
    return price + discount

result = calculate_discount(100, 20)
print(f"Discounted price: {result}")
print(f"Expected: 80, Got: {result}")
```

### Configuration
- Selected: **Strict Logical Rules**
- Max Iterations: **5**
- Optimize Efficiency: **Yes**

### Results
```
✅ Repair successful in 3 iterations!

Detected Errors:
- Line 4: Missing percentage division (/100)
- Line 5: Wrong operator (+ should be -)

Applied Patches:
- logical_patch_1: Fix percentage calculation
- logical_patch_2: Fix operator (+ to -)

Execution Time: 1.2s
Success Rate: 100%
```

### Fixed Code
```python
def calculate_discount(price, percent):
    '''Calculate final price after discount'''
    discount = price * percent / 100  # ✅ Added /100
    return price - discount           # ✅ Changed + to -

result = calculate_discount(100, 20)
print(f"Discounted price: {result}")
print(f"Expected: 80, Got: {result}")
```

### Output
```
Discounted price: 80.0
Expected: 80, Got: 80.0
```

---

## 🧪 Testing

### Verify Integration

```bash
# Run integration test
python3 test_streamlit_integration.py
```

Expected output:
```
✅ The Streamlit app is FULLY INTEGRATED with the backend!
✅ All modules imported successfully
✅ Real autonomous_repair() called
✅ Real DSL config loaded
✅ Real sandbox execution
✅ Real stdout/stderr captured
```

---

## 📚 Documentation

- **Integration Guide**: `STREAMLIT_INTEGRATION_GUIDE.md`
- **Comparison**: `INTEGRATION_COMPARISON.md`
- **Backend Docs**: `Backend/docs/`
- **DSL Guide**: `QUICKSTART_DSL.md`

---

## 🎉 Summary

The FixGoblin Streamlit app provides:

✅ **Modern Web Interface** - Clean, intuitive design  
✅ **Full Backend Integration** - Real debugging power  
✅ **Real-Time Results** - Live feedback  
✅ **Configurable** - DSL-based customization  
✅ **Production Ready** - No mock data  
✅ **User Friendly** - Simple 6-step workflow  

**Launch now and start debugging!** 🚀

```bash
./launch_streamlit.sh
```
