"""
AI Code Debugger - Streamlit UI (Integrated)
=============================================
A modern web interface for FixGoblin code debugging system.
Fully integrated with backend autonomous repair engine.
"""

import streamlit as st
import time
import sys
import os
import tempfile
import difflib
from pathlib import Path

# Add Backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)

# Import backend modules
from core.autonomous_repair import autonomous_repair
from core.dsl_parser import parse_dsl_config, validate_config, is_rule_allowed
from core.sandbox_runner import run_in_sandbox
from core.error_parser import parse_error
from core.logical_validator import validate_logic

# Import universal repair
sys.path.insert(0, os.path.dirname(__file__))
from universal_repair import universal_repair

# Page configuration
st.set_page_config(
    page_title="FixGoblin",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for next-gen glassmorphism styling
st.markdown("""
<style>
    /* === Page Background === */
    .stApp {
        background: #0B0F14;
        background-image: 
            radial-gradient(circle at 20% 10%, rgba(88, 101, 242, 0.08) 0%, transparent 40%),
            radial-gradient(circle at 80% 90%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(59, 130, 246, 0.04) 0%, transparent 60%);
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 3rem;
        max-width: 1400px;
    }
    
    /* Light mode background */
    @media (prefers-color-scheme: light) {
        .stApp {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            background-image: 
                radial-gradient(circle at 20% 10%, rgba(88, 101, 242, 0.03) 0%, transparent 40%),
                radial-gradient(circle at 80% 90%, rgba(139, 92, 246, 0.02) 0%, transparent 50%);
        }
    }
    
    /* === GLASSMORPHISM PANELS === */
    
    /* Column containers - subtle glass effect */
    [data-testid="column"] {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 1.5rem;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="column"] {
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.4);
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.5);
        }
    }
    
    /* Hover Effect on Glass Panels */
    [data-testid="column"]:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.12),
            0 0 40px rgba(88, 101, 242, 0.15);
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="column"]:hover {
            box-shadow: 
                0 12px 40px rgba(0, 0, 0, 0.15),
                inset 0 1px 0 rgba(255, 255, 255, 0.6),
                0 0 30px rgba(88, 101, 242, 0.2);
        }
    }
    
    /* === TYPOGRAPHY === */
    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 60px rgba(88, 101, 242, 0.5);
        letter-spacing: -0.02em;
    }
    
    @media (prefers-color-scheme: light) {
        .main-header {
            color: #1a1a1a;
            text-shadow: 0 0 40px rgba(88, 101, 242, 0.2);
        }
    }
    
    .subtitle-text {
        color: rgba(255, 255, 255, 0.7);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 3rem;
    }
    
    @media (prefers-color-scheme: light) {
        .subtitle-text {
            color: rgba(0, 0, 0, 0.6);
        }
    }
    
    .section-header {
        font-size: 1.6rem;
        font-weight: 600;
        color: #ffffff;
        margin-top: 2.5rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    @media (prefers-color-scheme: light) {
        .section-header {
            color: #1a1a1a;
            border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        }
    }
    
    /* Subheaders and labels */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    p, span, div, label, .stMarkdown {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    @media (prefers-color-scheme: light) {
        h1, h2, h3, h4, h5, h6 {
            color: #1a1a1a !important;
        }
        
        p, span, div, label, .stMarkdown {
            color: rgba(0, 0, 0, 0.87) !important;
        }
    }
    
    /* === NOTIFICATION BOXES === */
    .success-box, .error-box, .info-box {
        padding: 1.25rem;
        border-radius: 20px;
        margin: 1.5rem 0;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        border: 1px solid;
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.04),
            0 20px 50px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        animation: slideInUp 0.5s ease-out;
    }
    
    .success-box {
        background: rgba(34, 197, 94, 0.12);
        border-color: rgba(34, 197, 94, 0.3);
        color: #ffffff;
    }
    
    .error-box {
        background: rgba(239, 68, 68, 0.12);
        border-color: rgba(239, 68, 68, 0.3);
        color: #ffffff;
    }
    
    .info-box {
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(59, 130, 246, 0.3);
        color: #ffffff;
    }
    
    @media (prefers-color-scheme: light) {
        .success-box {
            background: rgba(34, 197, 94, 0.08);
            border-color: rgba(34, 197, 94, 0.25);
            color: #166534;
        }
        
        .error-box {
            background: rgba(239, 68, 68, 0.08);
            border-color: rgba(239, 68, 68, 0.25);
            color: #991b1b;
        }
        
        .info-box {
            background: rgba(59, 130, 246, 0.08);
            border-color: rgba(59, 130, 246, 0.25);
            color: #1e40af;
        }
    }
    
    /* === BUTTONS === */
    .stButton > button {
        background: rgba(88, 101, 242, 0.15);
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        padding: 0.875rem 2.5rem;
        border-radius: 20px;
        border: 1px solid rgba(88, 101, 242, 0.3);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.04),
            0 20px 50px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    @media (prefers-color-scheme: light) {
        .stButton > button {
            background: rgba(88, 101, 242, 0.1);
            color: #1a1a1a;
            border: 1px solid rgba(88, 101, 242, 0.25);
            box-shadow: 
                0 0 0 1px rgba(255, 255, 255, 0.2),
                0 20px 50px rgba(0, 0, 0, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
    }
    
    /* Button Sheen Effect */
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 
            0 0 0 1px rgba(88, 101, 242, 0.4),
            0 0 60px rgba(88, 101, 242, 0.4),
            0 25px 60px rgba(0, 0, 0, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.15);
        border-color: rgba(88, 101, 242, 0.5);
        background: rgba(88, 101, 242, 0.25);
    }
    
    @media (prefers-color-scheme: light) {
        .stButton > button:hover {
            box-shadow: 
                0 0 0 1px rgba(88, 101, 242, 0.3),
                0 0 40px rgba(88, 101, 242, 0.25),
                0 25px 60px rgba(0, 0, 0, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.4);
            background: rgba(88, 101, 242, 0.18);
        }
    }
    
    .stButton > button:active {
        transform: scale(0.98);
    }
    
    /* Primary Button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(88, 101, 242, 0.3), rgba(139, 92, 246, 0.3));
        border: 1px solid rgba(88, 101, 242, 0.5);
    }
    
    @media (prefers-color-scheme: light) {
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, rgba(88, 101, 242, 0.2), rgba(139, 92, 246, 0.2));
        }
    }
    
    /* === INPUT FIELDS === */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        backdrop-filter: blur(15px) saturate(180%);
        -webkit-backdrop-filter: blur(15px) saturate(180%);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (prefers-color-scheme: light) {
        .stTextInput > div > div > input,
        .stTextArea textarea,
        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.6) !important;
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            color: #1a1a1a !important;
        }
    }
    
    .stTextInput > div > div > input:hover,
    .stTextArea textarea:hover {
        border-color: rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 0 30px rgba(255, 255, 255, 0.15);
    }
    
    @media (prefers-color-scheme: light) {
        .stTextInput > div > div > input:hover,
        .stTextArea textarea:hover {
            border-color: rgba(88, 101, 242, 0.3) !important;
            box-shadow: 0 0 20px rgba(88, 101, 242, 0.1);
        }
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(88, 101, 242, 0.5) !important;
        box-shadow: 0 0 40px rgba(88, 101, 242, 0.3) !important;
        outline: none !important;
    }
    
    /* === FILE UPLOAD DROP ZONE === */
    [data-testid="stFileUploader"] section {
        background: rgba(255, 255, 255, 0.04);
        border: 2px dashed rgba(255, 255, 255, 0.15) !important;
        border-radius: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stFileUploader"] section {
            background: rgba(255, 255, 255, 0.4);
            border: 2px dashed rgba(0, 0, 0, 0.15) !important;
        }
    }
    
    [data-testid="stFileUploader"] section:hover {
        border-color: rgba(88, 101, 242, 0.4) !important;
        box-shadow: 0 0 40px rgba(88, 101, 242, 0.2);
        background: rgba(88, 101, 242, 0.08);
    }
    
    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(40px) saturate(180%);
        -webkit-backdrop-filter: blur(40px) saturate(180%);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.7);
            border-right: 1px solid rgba(0, 0, 0, 0.08);
        }
    }
    
    [data-testid="stSidebar"] h2 {
        color: #ffffff;
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stSidebar"] h2 {
            color: #1a1a1a;
        }
    }
    
    /* === CODE BLOCKS === */
    .stCodeBlock {
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }
    
    @media (prefers-color-scheme: light) {
        .stCodeBlock {
            background: rgba(0, 0, 0, 0.04) !important;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
    }
    
    /* === METRICS === */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1rem;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.04),
            0 15px 40px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(0, 0, 0, 0.08);
            box-shadow: 
                0 0 0 1px rgba(255, 255, 255, 0.2),
                0 15px 40px rgba(0, 0, 0, 0.08),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 0 0 1px rgba(255, 255, 255, 0.08),
            0 20px 50px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stMetric"] label {
        color: rgba(255, 255, 255, 0.7) !important;
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stMetric"] label {
            color: rgba(0, 0, 0, 0.6) !important;
        }
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    @media (prefers-color-scheme: light) {
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #1a1a1a !important;
        }
    }
    
    /* === EXPANDERS === */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        color: #ffffff !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @media (prefers-color-scheme: light) {
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(0, 0, 0, 0.08);
            color: #1a1a1a !important;
        }
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(88, 101, 242, 0.3);
        box-shadow: 0 0 30px rgba(88, 101, 242, 0.15);
    }
    
    /* === DIVIDERS === */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 2rem 0;
    }
    
    @media (prefers-color-scheme: light) {
        hr {
            border-color: rgba(0, 0, 0, 0.08) !important;
        }
    }
    
    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Apply subtle animations */
    .main-header, .subtitle-text {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }
    
    @media (prefers-color-scheme: light) {
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.02);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(0, 0, 0, 0.15);
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(0, 0, 0, 0.25);
        }
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-header">🔮 FixGoblin</div>', unsafe_allow_html=True)
st.markdown("<p class='subtitle-text'>AI-Powered Autonomous Code Repair</p>", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Config dropdown with custom input option
    config_options = [
        "Default (No restrictions)",
        "Strict Logical Rules",
        "Conservative Mode",
        "Aggressive Mode",
        "Custom Config..."
    ]
    
    selected_config = st.selectbox(
        "Select Debug Configuration",
        config_options,
        help="Choose a predefined config or enter custom"
    )
    
    # If custom is selected, show text input
    custom_config = ""
    if selected_config == "Custom Config...":
        custom_config = st.text_input(
            "Enter custom config file path",
            placeholder="e.g., my_rules.dsl"
        )
    
    st.divider()
    
    # Efficiency toggle
    optimize_efficiency = st.toggle(
        "Improve code efficiency?",
        value=False,
        help="Enable efficiency optimization patches"
    )
    
    # Max iterations slider
    max_iterations = st.slider(
        "Max Repair Iterations",
        min_value=1,
        max_value=10,
        value=5,
        help="Maximum number of repair attempts"
    )
    
    st.divider()
    
    # Info section
    st.info("💡 **Tip:** Upload a file or paste code below to get started!")

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload Source Code")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["py", "js", "java", "cpp", "c", "cc", "cxx", "go", "txt"],
        help="Upload your source code file - ALL LANGUAGES SUPPORTED!"
    )
    
    if uploaded_file is not None:
        file_ext = uploaded_file.name.split('.')[-1].lower()
        
        # Language support map
        lang_support = {
            'py': '🐍 Python',
            'cpp': '⚡ C++',
            'cc': '⚡ C++',
            'cxx': '⚡ C++',
            'c': '🔧 C',
            'java': '☕ Java',
            'js': '📜 JavaScript',
            'go': '🔵 Go'
        }
        
        lang_name = lang_support.get(file_ext, f'📄 {file_ext.upper()}')
        st.success(f"✅ File uploaded: **{uploaded_file.name}** ({lang_name})")
        st.info(f"✨ **Full auto-repair available for Python, C++, Java, and JavaScript!**")
        
        file_content = uploaded_file.read().decode("utf-8")
        
        # Detect language for syntax highlighting
        lang_map = {'py': 'python', 'cpp': 'cpp', 'cc': 'cpp', 'cxx': 'cpp', 'c': 'c', 'java': 'java', 'js': 'javascript', 'go': 'go'}
        display_lang = lang_map.get(file_ext, 'python')
        
        st.code(file_content, language=display_lang, line_numbers=True)

with col2:
    st.subheader("Edit Or Paste Code Here")
    code_input = st.text_area(
        "Enter your code",
        height=300,
        placeholder="def calculate_discount(price, percent):\n    discount = price * percent  # Bug!\n    return price + discount  # Bug!",
        help="Type or paste your code here"
    )

# Determine which code to use
code_to_debug = ""
file_extension = "py"  # Default to Python

if uploaded_file is not None:
    code_to_debug = file_content
    file_extension = uploaded_file.name.split('.')[-1].lower()
elif code_input:
    code_to_debug = code_input
    file_extension = "py"

# Show language support info
if code_to_debug:
    lang_emoji = {
        'py': '🐍 Python',
        'cpp': '⚡ C++',
        'cc': '⚡ C++',
        'cxx': '⚡ C++',
        'c': '🔧 C',
        'java': '☕ Java',
        'js': '📜 JavaScript',
        'go': '🔵 Go'
    }
    
    if file_extension in ['py', 'cpp', 'cc', 'cxx', 'c', 'java', 'js']:
        st.success(f"""
        ✅ **Full Auto-Repair Available for {lang_emoji.get(file_extension, file_extension.upper())}**
        
        FixGoblin will automatically:
        - 🔍 Detect errors (syntax, runtime, logical)
        - 🔧 Generate fix patches
        - ✅ Test and apply working fixes
        - 📦 Create backup of original code
        """)
    elif file_extension == 'go':
        st.info(f"ℹ️ **{lang_emoji.get(file_extension, file_extension.upper())}**: Error detection available. Full auto-repair coming soon!")

# Run Debugger Button
st.divider()
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    run_button = st.button("Start Debugging", use_container_width=True, type="primary")

# Results section
if run_button:
    if not code_to_debug:
        st.error("⚠️ Please upload a file or paste code before running the debugger!")
    else:
        # Initialize session state for results
        if 'repair_result' not in st.session_state:
            st.session_state.repair_result = None
        
        # Create temporary file for code with correct extension
        temp_file = None
        try:
            suffix_map = {
                'py': '.py',
                'cpp': '.cpp', 'cc': '.cpp', 'cxx': '.cpp',
                'c': '.c',
                'java': '.java',
                'js': '.js',
                'go': '.go'
            }
            suffix = suffix_map.get(file_extension, '.py')
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
                f.write(code_to_debug)
                temp_file = f.name
            
            # Load DSL configuration
            config = None
            config_path = None
            
            if selected_config != "Default (No restrictions)" and selected_config != "Custom Config...":
                # Map selection to actual DSL files
                config_map = {
                    "Strict Logical Rules": "strict_logical_rules.dsl",
                    "Conservative Mode": "debug_rules.dsl",
                    "Aggressive Mode": "debug_rules_minimal.dsl"
                }
                config_path = config_map.get(selected_config)
                
                if config_path and os.path.exists(config_path):
                    try:
                        config = parse_dsl_config(config_path)
                        st.info(f"📋 Using configuration: **{selected_config}**")
                    except Exception as e:
                        st.warning(f"⚠️ Could not load config: {e}. Using defaults.")
            
            elif selected_config == "Custom Config..." and custom_config:
                if os.path.exists(custom_config):
                    try:
                        config = parse_dsl_config(custom_config)
                        st.info(f"📋 Using custom configuration: **{custom_config}**")
                    except Exception as e:
                        st.error(f"❌ Error loading custom config: {e}")
                        st.stop()
                else:
                    st.error(f"❌ Custom config file not found: {custom_config}")
                    st.stop()
            
            # Show progress
            progress_container = st.empty()
            with progress_container:
                with st.spinner("🔍 Running autonomous repair..."):
                    progress_bar = st.progress(0)
                    
                    # Run autonomous repair (universal for all languages)
                    start_time = time.time()
                    
                    # Use universal_repair for all languages (it handles Python too)
                    result = universal_repair(
                        file_path=temp_file,
                        max_iterations=max_iterations,
                        language=None  # Auto-detect from extension
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Update progress
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        time.sleep(0.005)
            
            progress_container.empty()
            
            # Store result in session state
            st.session_state.repair_result = result
            st.session_state.execution_time = execution_time
            st.session_state.original_code = code_to_debug
            
            # Read final code
            with open(temp_file, 'r', encoding='utf-8') as f:
                final_code = f.read()
            
            st.session_state.final_code = final_code
            
            # Show success or failure
            if result['success']:
                if result['total_iterations'] == 0:
                    st.success(f"🎉 **CODE IS ALREADY PERFECT!** No errors found - your code works correctly!")
                else:
                    st.success(f"✅ Repair successful in {result['total_iterations']} iteration(s)!")
            else:
                st.error(f"❌ Repair failed: {result['reason']}")
        
        except Exception as e:
            st.error(f"❌ Error during execution: {str(e)}")
            import traceback
            with st.expander("🔍 View Error Details"):
                st.code(traceback.format_exc())
        
        finally:
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

        # Display results if available
        if 'repair_result' in st.session_state and st.session_state.repair_result:
            result = st.session_state.repair_result
            
            st.divider()
            
            # If code was already perfect, show special message
            if result['success'] and result['total_iterations'] == 0:
                st.balloons()
                st.markdown("""
                ### 🎉 Your Code is Perfect!
                
                No errors detected. Your code:
                - ✅ Compiles successfully
                - ✅ Runs without errors
                - ✅ Produces correct output
                
                **No repairs needed!**
                """)
                
                # Show the code
                st.markdown('<div class="section-header">📄 Your Code</div>', unsafe_allow_html=True)
                st.code(st.session_state.get('original_code', ''), language='cpp', line_numbers=True)
                
            else:
                # Section 1: Execution Output
                st.markdown('<div class="section-header">📤 Execution Output</div>', unsafe_allow_html=True)
                
                # Get output from last iteration if available
                stdout_output = ""
                stderr_output = ""
                
                if result['iterations']:
                    # Try to run final code to get output
                    try:
                        # Create temp file with final code
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                            f.write(st.session_state.final_code)
                            temp_path = f.name
                        
                        # Run in sandbox
                        sandbox_result = run_in_sandbox(temp_path)
                        stdout_output = sandbox_result.get('stdout', '').strip()
                        stderr_output = sandbox_result.get('stderr', '').strip()
                        
                        # Cleanup
                        os.unlink(temp_path)
                    except Exception as e:
                        stdout_output = f"(Could not capture output: {str(e)})"
                        stderr_output = ""
                
                col_out1, col_out2 = st.columns(2)
            
            with col_out1:
                st.markdown("**Standard Output (stdout):**")
                if stdout_output:
                    st.code(stdout_output, language="text")
                else:
                    st.info("(no output)")
            
            with col_out2:
                st.markdown("**Standard Error (stderr):**")
                if stderr_output:
                    st.code(stderr_output, language="text")
                else:
                    st.info("(no errors in stderr)")
            
            # Section 2: Detected Errors
            st.markdown('<div class="section-header">🐛 Detected Errors</div>', unsafe_allow_html=True)
            
            if result['iterations'] and len(result['iterations']) > 0:
                # Show errors from iterations
                iterations_with_errors = [it for it in result['iterations'] if it.get('error_type')]
                
                if iterations_with_errors:
                    # Show first error details
                    first_error = iterations_with_errors[0]
                    
                    error_col1, error_col2, error_col3 = st.columns(3)
                    
                    with error_col1:
                        st.metric("Error Type", first_error.get('error_type', 'Unknown'))
                    
                    with error_col2:
                        line_num = first_error.get('line_number', 'N/A')
                        st.metric("Line Number", line_num)
                    
                    with error_col3:
                        priority = "HIGH" if first_error.get('error_type') == 'LogicalError' else "MEDIUM"
                        st.metric("Priority", priority)
                    
                    st.markdown('<div class="error-box">', unsafe_allow_html=True)
                    st.markdown("**Error Message:**")
                    error_msg = first_error.get('error_message', 'No message available')
                    st.markdown(f"`{error_msg}`")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Additional error details
                    with st.expander("🔍 View All Detected Issues"):
                        st.markdown(f"**Total Errors Fixed:** {len(iterations_with_errors)}")
                        for idx, it in enumerate(iterations_with_errors, 1):
                            st.markdown(f"**Issue {idx}:**")
                            st.markdown(f"- **Type:** {it.get('error_type', 'Unknown')}")
                            st.markdown(f"- **Line:** {it.get('line_number', 'N/A')}")
                            st.markdown(f"- **Message:** {it.get('error_message', 'N/A')}")
                            st.markdown(f"- **Action:** {it.get('description', 'N/A')}")
                            st.divider()
                else:
                    st.info("✅ No errors detected - code runs successfully!")
            else:
                st.info("ℹ️ No error information available")
            
            # Section 3: Applied Patches
            st.markdown('<div class="section-header">🔧 Applied Patches</div>', unsafe_allow_html=True)
            
            if result['iterations']:
                patches_applied = [it for it in result['iterations'] if it.get('selected_patch_id')]
                
                if patches_applied:
                    st.markdown(f"**Total Patches Applied:** {len(patches_applied)}")
                    
                    for idx, patch_info in enumerate(patches_applied, 1):
                        with st.expander(f"📦 Patch {idx}: {patch_info.get('selected_patch_id', 'unknown')}", expanded=(idx==1)):
                            patch_col1, patch_col2 = st.columns([3, 1])
                            
                            with patch_col1:
                                st.markdown(f"**Patch ID:** `{patch_info.get('selected_patch_id', 'unknown')}`")
                                st.markdown(f"**Description:** {patch_info.get('description', 'N/A')}")
                            
                            with patch_col2:
                                score = patch_info.get('patch_score', 0)
                                st.metric("Score", f"{score}", delta="Applied")
                            
                            # Show iteration details
                            st.markdown("**Changes Made:**")
                            st.markdown(f"- Error Type: {patch_info.get('error_type', 'N/A')}")
                            st.markdown(f"- Line: {patch_info.get('line_number', 'N/A')}")
                            st.markdown(f"- Status: {patch_info.get('status', 'N/A').upper()}")
                else:
                    st.info("✅ No patches needed - code was already correct!")
            else:
                st.info("ℹ️ No patch information available")
            
            # Section 4: Before / After Code Diff
            st.markdown('<div class="section-header">📊 Before / After Code Diff</div>', unsafe_allow_html=True)
            
            # Generate unified diff
            original_lines = st.session_state.original_code.splitlines(keepends=True)
            final_lines = st.session_state.final_code.splitlines(keepends=True)
            
            diff = list(difflib.unified_diff(
                original_lines,
                final_lines,
                fromfile='Original Code',
                tofile='Fixed Code',
                lineterm=''
            ))
            
            if len(diff) > 2:  # Has actual differences
                # Show unified diff
                st.markdown("**Unified Diff:**")
                diff_text = '\n'.join(diff)
                st.code(diff_text, language="diff")
                
                st.divider()
                
                # Show side-by-side comparison
                diff_col1, diff_col2 = st.columns(2)
                
                with diff_col1:
                    st.markdown("**❌ Before (Original Code):**")
                    st.code(st.session_state.original_code, language="python", line_numbers=True)
                
                with diff_col2:
                    st.markdown("**✅ After (Fixed Code):**")
                    st.code(st.session_state.final_code, language="python", line_numbers=True)
            else:
                st.info("ℹ️ No changes were made to the code")
            
            # Summary section
            st.divider()
            st.markdown('<div class="section-header">📋 Repair Summary</div>', unsafe_allow_html=True)
            
            summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
            
            with summary_col1:
                st.metric("Iterations", result['total_iterations'], help="Number of repair iterations")
            
            with summary_col2:
                patches_count = len([it for it in result['iterations'] if it.get('selected_patch_id')])
                st.metric("Patches Applied", patches_count, help="Number of patches applied")
            
            with summary_col3:
                success_pct = "100%" if result['success'] else "0%"
                delta_text = "Success" if result['success'] else "Failed"
                st.metric("Success Rate", success_pct, delta=delta_text)
            
            with summary_col4:
                exec_time = st.session_state.execution_time
                st.metric("Execution Time", f"{exec_time:.2f}s", help="Total execution time")
            
            # Action buttons
            st.divider()
            action_col1, action_col2, action_col3, action_col4 = st.columns(4)
            
            with action_col1:
                if st.button("💾 Download Fixed Code", use_container_width=True):
                    # Provide download button for fixed code
                    st.download_button(
                        label="⬇️ Download",
                        data=st.session_state.final_code,
                        file_name="fixed_code.py",
                        mime="text/plain"
                    )
            
            with action_col2:
                # Copy to clipboard using text area (user can copy manually)
                if st.button("📋 View Fixed Code", use_container_width=True):
                    st.text_area("Fixed Code (Copy this)", st.session_state.final_code, height=200)
            
            with action_col3:
                if st.button("📄 View JSON Report", use_container_width=True):
                    import json
                    st.json(result)
            
            with action_col4:
                if st.button("🔄 Clear Results", use_container_width=True):
                    st.session_state.repair_result = None
                    st.rerun()
            
            # Configuration used
            st.divider()
            with st.expander("⚙️ View Configuration Used"):
                st.markdown(f"""
                **Selected Config:** {selected_config}
                {'**Custom Path:** ' + custom_config if custom_config else ''}
                **Optimize Efficiency:** {'Yes' if optimize_efficiency else 'No'}
                **Max Iterations:** {max_iterations}
                **Final Status:** {result['final_status']}
                **Reason:** {result['reason']}
                """)
                
                # Show DSL config if loaded
                if config:
                    st.markdown("**DSL Configuration:**")
                    st.markdown(f"- **Allowed Rules:** {len(config.get('allow', set()))}")
                    if config.get('allow'):
                        for rule in sorted(config['allow']):
                            st.markdown(f"  - ✓ {rule}")
                    
                    st.markdown(f"- **Denied Rules:** {len(config.get('deny', set()))}")
                    if config.get('deny'):
                        for rule in sorted(config['deny']):
                            st.markdown(f"  - ✗ {rule}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <p style="color: rgba(255, 255, 255, 0.7); font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">
        <strong style="background: linear-gradient(135deg, #ffffff 0%, rgba(255, 255, 255, 0.6) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">FixGoblin</strong> | AI-Powered Autonomous Code Repair v2.0
    </p>
    <p style="color: rgba(255, 255, 255, 0.5); font-size: 0.95rem;">
        🔧 Multi-Language Debugger with Syntax & Logical Error Detection | 🛡️ Secure Sandboxed Execution
    </p>
</div>
<style>
    @media (prefers-color-scheme: light) {
        div[style*="text-align: center"] p:first-of-type {
            color: rgba(0, 0, 0, 0.7) !important;
        }
        div[style*="text-align: center"] p:first-of-type strong {
            background: linear-gradient(135deg, #1a1a1a 0%, #4a4a4a 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        div[style*="text-align: center"] p:last-of-type {
            color: rgba(0, 0, 0, 0.5) !important;
        }
    }
</style>
""", unsafe_allow_html=True)
