# Backend Directory Structure

## 📁 Organization

```
backend/
├── core/              # Core autonomous debugging modules
│   ├── __init__.py
│   ├── sandbox_runner.py
│   ├── error_parser.py
│   ├── patch_generator.py
│   ├── patch_optimizer.py
│   ├── autonomous_repair.py
│   └── logical_validator.py
│
├── backups/           # Backup files created during repairs
│   └── *.backup
│
├── logs/              # JSON repair logs and execution history
│   └── *.json
│
├── docs/              # Documentation files
│   ├── ARCHITECTURE.md
│   ├── QUICKSTART.md
│   └── SYSTEM_FLOW.md
│
├── demos/             # Demo and step-by-step examples
│   └── step*.py
│
└── tests/             # Test files and sample buggy code
    ├── user.py
    ├── multi_line_buggy.py
    └── new_test_code.py
```

## 🎯 Purpose

- **core/**: Main system components for autonomous debugging
- **backups/**: Safe storage of original files before modifications
- **logs/**: Detailed JSON logs of repair operations
- **docs/**: System documentation and guides
- **demos/**: Example scripts demonstrating features
- **tests/**: Sample files for testing the system
