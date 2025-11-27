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

# Page configuration
st.set_page_config(
    page_title="FixGoblin",
    page_icon="",
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
st.markdown('<div class="main-header">FixGoblin</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#7f8c8d; font-size:1.1rem;'>AI-Powered Autonomous Code Repair</p>", unsafe_allow_html=True)

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
    st.subheader("Edit Or Paste Code Here")
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
    run_button = st.button("Start Debugging", use_container_width=True, type="primary")

# Results section
if run_button:
    if not code_to_debug:
        st.error("⚠️ Please upload a file or paste code before running the debugger!")
    else:
        # Initialize session state for results
        if 'repair_result' not in st.session_state:
            st.session_state.repair_result = None
        
        # Create temporary file for code
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
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
                    
                    # Run autonomous repair
                    start_time = time.time()
                    
                    result = autonomous_repair(
                        file_path=temp_file,
                        max_iterations=max_iterations,
                        optimize_efficiency=optimize_efficiency
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
<div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
    <p><strong>FixGoblin</strong> | AI-Powered Autonomous Code Repair v2.0</p>
    <p>🔧 Multi-Language Debugger with Syntax & Logical Error Detection | 🛡️ Secure Sandboxed Execution</p>
</div>
""", unsafe_allow_html=True)
