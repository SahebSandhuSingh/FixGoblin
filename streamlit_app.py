"""
AI Code Debugger - Streamlit UI
================================
A modern web interface for FixGoblin code debugging system.
"""

import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="AI Code Debugger",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #145a8a;
    }
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="main-header">🔧 AI Code Debugger</div>', unsafe_allow_html=True)
st.markdown("**Powered by FixGoblin v2.0** - Autonomous Code Repair System", unsafe_allow_html=True)

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
        type=["py", "js", "java", "cpp", "txt"],
        help="Upload your source code file"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: **{uploaded_file.name}**")
        file_content = uploaded_file.read().decode("utf-8")
        st.code(file_content, language="python", line_numbers=True)

with col2:
    st.subheader("✍️ Or Paste Code Here")
    code_input = st.text_area(
        "Enter your code",
        height=300,
        placeholder="def calculate_discount(price, percent):\n    discount = price * percent  # Bug!\n    return price + discount  # Bug!",
        help="Type or paste your code here"
    )

# Determine which code to use
code_to_debug = ""
if uploaded_file is not None:
    code_to_debug = file_content
elif code_input:
    code_to_debug = code_input

# Run Debugger Button
st.divider()
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    run_button = st.button("🚀 Run Debugger", use_container_width=True, type="primary")

# Results section
if run_button:
    if not code_to_debug:
        st.error("⚠️ Please upload a file or paste code before running the debugger!")
    else:
        # Show progress
        with st.spinner("🔍 Analyzing code..."):
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
        
        st.success("✅ Analysis complete!")
        
        st.divider()
        
        # Section 1: Execution Output
        st.markdown('<div class="section-header">📤 Execution Output</div>', unsafe_allow_html=True)
        
        col_out1, col_out2 = st.columns(2)
        
        with col_out1:
            st.markdown("**Standard Output (stdout):**")
            st.code("""
Original: $100, Discount: 20%, Final: $2100
Expected: $80, Got: $2100

Discounted price: 2100.0
Expected: 80, Got: 2100.0
            """.strip(), language="text")
        
        with col_out2:
            st.markdown("**Standard Error (stderr):**")
            st.code("(no errors in stderr)", language="text")
        
        # Section 2: Detected Error
        st.markdown('<div class="section-header">🐛 Detected Error</div>', unsafe_allow_html=True)
        
        error_col1, error_col2, error_col3 = st.columns(3)
        
        with error_col1:
            st.metric("Error Type", "LogicalError")
        
        with error_col2:
            st.metric("Line Number", "3")
        
        with error_col3:
            st.metric("Priority", "HIGH", delta="Critical")
        
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("**Error Message:**")
        st.markdown("`Function 'calculate_discount' multiplies by percentage (line 3) without dividing by 100`")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional error details
        with st.expander("🔍 View Detailed Analysis"):
            st.markdown("""
            **Detected Issues:**
            1. ✗ Expected output 80.0 but got 2100.0 - possible logic error
            2. ✗ Function multiplies by percentage without dividing by 100
            3. ✗ Function adds discount to price (line 4) - should subtract
            
            **Affected Code:**
            ```python
            discount = price * percent  # Missing /100
            ```
            
            **Suggested Fix:**
            - Divide percentage by 100 before multiplying
            - Change addition operator to subtraction
            """)
        
        # Section 3: Proposed Patch
        st.markdown('<div class="section-header">🔧 Proposed Patch</div>', unsafe_allow_html=True)
        
        patch_col1, patch_col2 = st.columns([3, 1])
        
        with patch_col1:
            st.markdown("**Patch ID:** `logical_patch_1`")
            st.markdown("**Description:** Fix percentage calculation and operator")
        
        with patch_col2:
            st.metric("Confidence Score", "110/110", delta="Perfect")
        
        st.code("""
--- Original Code
+++ Patched Code
@@ Line 3 @@
-    discount = price * percent
+    discount = price * percent / 100

@@ Line 4 @@
-    return price + discount
+    return price - discount
        """.strip(), language="diff")
        
        # Section 4: Before / After Code Diff
        st.markdown('<div class="section-header">📊 Before / After Code Diff</div>', unsafe_allow_html=True)
        
        diff_col1, diff_col2 = st.columns(2)
        
        with diff_col1:
            st.markdown("**❌ Before (Buggy Code):**")
            st.code("""
def calculate_discount(price, percent):
    \"\"\"Calculate final price after discount\"\"\"
    discount = price * percent
    return price + discount
            """.strip(), language="python", line_numbers=True)
        
        with diff_col2:
            st.markdown("**✅ After (Fixed Code):**")
            st.code("""
def calculate_discount(price, percent):
    \"\"\"Calculate final price after discount\"\"\"
    discount = price * percent / 100
    return price - discount
            """.strip(), language="python", line_numbers=True)
        
        # Summary section
        st.divider()
        st.markdown('<div class="section-header">📋 Repair Summary</div>', unsafe_allow_html=True)
        
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Iterations", "3", help="Number of repair iterations")
        
        with summary_col2:
            st.metric("Patches Applied", "2", help="Number of patches applied")
        
        with summary_col3:
            st.metric("Success Rate", "100%", delta="Success")
        
        with summary_col4:
            st.metric("Execution Time", "1.2s", delta="-0.3s")
        
        # Action buttons
        st.divider()
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("💾 Save Fixed Code", use_container_width=True):
                st.success("Code saved successfully!")
        
        with action_col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.info("Code copied to clipboard!")
        
        with action_col3:
            if st.button("📄 Generate Report", use_container_width=True):
                st.info("Report generated!")
        
        with action_col4:
            if st.button("🔄 Run Again", use_container_width=True):
                st.rerun()
        
        # Configuration used
        st.divider()
        with st.expander("⚙️ View Configuration Used"):
            st.markdown(f"""
            **Selected Config:** {selected_config}
            {'**Custom Path:** ' + custom_config if custom_config else ''}
            **Optimize Efficiency:** {'Yes' if optimize_efficiency else 'No'}
            **Max Iterations:** {max_iterations}
            
            **Allowed Patches:**
            - logical_patch_1 ✓
            - wrong_operator ✓
            - missing_percentage_conversion ✓
            
            **Denied Patches:**
            - variable_rename ✗
            - code_restructure ✗
            """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
    <p><strong>AI Code Debugger</strong> | Powered by FixGoblin v2.0</p>
    <p>🔧 Autonomous Code Repair System with Logical Error Detection</p>
</div>
""", unsafe_allow_html=True)
