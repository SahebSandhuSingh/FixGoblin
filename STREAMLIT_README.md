# 🎨 AI Code Debugger - Streamlit UI

## Quick Start

### 1. Install Streamlit
```bash
pip install streamlit
# OR
pip install -r requirements_streamlit.txt
```

### 2. Run the App
```bash
streamlit run streamlit_app.py
```

### 3. Open Browser
The app will automatically open at `http://localhost:8501`

---

## Features

✅ **File Upload** - Upload .py, .js, .java, .cpp, .txt files  
✅ **Code Editor** - Paste code directly in the text area  
✅ **Config Selection** - Dropdown with predefined + custom configs  
✅ **Efficiency Toggle** - Switch to enable optimization  
✅ **Real-time Results** - See execution output, errors, and patches  
✅ **Before/After Diff** - Visual code comparison  
✅ **Modern UI** - Clean, responsive design  

---

## UI Sections

### Input Area
- 📁 File uploader (left)
- ✍️ Code text area (right)

### Configuration Sidebar
- 🎯 Config selection dropdown
- ⚡ Efficiency toggle (Yes/No)
- 🔢 Max iterations slider

### Results Display
1. **📤 Execution Output** - stdout/stderr
2. **🐛 Detected Error** - Type, line, message
3. **🔧 Proposed Patch** - Code fix with diff
4. **📊 Before/After Diff** - Side-by-side comparison
5. **📋 Repair Summary** - Metrics and stats

### Action Buttons
- 💾 Save Fixed Code
- 📋 Copy to Clipboard
- 📄 Generate Report
- 🔄 Run Again

---

## Mock Data

The app uses **placeholder/mock data** - no real ML/LLM calls are made.

This is a UI prototype showing how FixGoblin results would be displayed.

---

## Customization

Edit `streamlit_app.py` to:
- Change colors (CSS section)
- Modify mock results
- Add new sections
- Integrate real FixGoblin backend

---

## Screenshot Preview

When you run the app, you'll see:
- Clean modern interface
- Blue and white color scheme
- Responsive layout
- Interactive elements
- Professional design

Enjoy! 🚀
