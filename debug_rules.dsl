# FixGoblin Debug Rules Configuration
# =====================================
# This file defines which debugging rules are allowed/denied
# and sets optimization parameters for the debugging pipeline.

# Allow specific patch types
allow: range_fix
allow: bounds_check
allow: logical_patch_1
allow: patch_0
allow: patch_1

# Deny certain risky operations
deny: variable_rename
deny: code_restructure

# Enable efficiency optimizations
optimize_efficiency: true

# Maximum number of patches to generate per iteration
max_patches: 3
