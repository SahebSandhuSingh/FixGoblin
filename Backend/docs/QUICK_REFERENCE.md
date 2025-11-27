# FixGoblin Quick Reference

## 🚀 One-Line Commands

```bash
# Basic repair with final report
python fixgoblin.py your_file.py --final-report

# Full featured repair
python fixgoblin.py your_file.py --final-report --log logs/repair.json --max-iterations 5

# Quiet mode with report
python fixgoblin.py your_file.py --final-report --quiet
```

## 📋 All CLI Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--final-report` | Generate comprehensive debugging report | `--final-report` |
| `--log FILE` | Save repair log to JSON file | `--log logs/repair.json` |
| `--max-iterations N` | Set max repair attempts (default: 5) | `--max-iterations 3` |
| `--optimize` | Enable efficiency optimization patches | `--optimize` |
| `--quiet` | Suppress detailed output | `--quiet` |

## 📊 Output Locations

| Type | Location | Format |
|------|----------|--------|
| Terminal Report | stdout | Colored text with emojis |
| JSON Report | `backend/logs/{filename}_final_report.json` | Structured JSON |
| Repair Log | `backend/logs/{custom_name}.json` | Iteration history |
| Backups | Same directory as original file | `.backup` extension |

## 🎯 Report Contents

### Terminal Output Sections
1. ✅ **Status**: Fixed / Partial / Failed
2. 🐛 **Errors**: All detected error types
3. 🔧 **Patches**: Applied fixes with scores
4. 📄 **Changes**: Line counts and diff preview
5. ⏱️ **Metadata**: File, time, iterations, timestamp

### JSON Report Fields
```json
{
  "metadata": {/* file, timestamp, time, iterations */},
  "status": {/* emoji, text, success, final_status */},
  "errors": {/* types, count */},
  "patches": {/* count, summaries */},
  "code_changes": {/* diff, line_counts */},
  "logs": {/* stdout, stderr */},
  "original_code": "...",
  "final_code": "..."
}
```

## 🔧 Common Use Cases

### 1. Quick Bug Fix
```bash
python fixgoblin.py buggy_code.py --final-report
```

### 2. CI/CD Integration
```bash
python fixgoblin.py src/app.py --final-report --log ci_logs/repair_$(date +%s).json --quiet
```

### 3. Development with Tracking
```bash
python fixgoblin.py dev/feature.py --final-report --log dev/logs/feature_repair.json
```

### 4. Limited Iterations for Speed
```bash
python fixgoblin.py quick_fix.py --final-report --max-iterations 2
```

### 5. Comprehensive Analysis
```bash
python fixgoblin.py complex_code.py --final-report --log full_analysis.json --max-iterations 10
```

## 📖 Documentation Files

| File | Purpose | Location |
|------|---------|----------|
| `FINAL_REPORT.md` | Complete usage guide | `backend/docs/` |
| `CHANGELOG.md` | Version history | `backend/docs/` |
| `IMPLEMENTATION_SUMMARY.md` | Technical details | `backend/docs/` |
| `QUICKSTART.md` | Getting started | `backend/docs/` |
| `ARCHITECTURE.md` | System design | `backend/docs/` |
| `README.md` | Main overview | Project root |

## 🎨 Terminal Colors

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 Green | Added lines | `+ new_code()` |
| 🔴 Red | Removed lines | `- old_code()` |
| 🔵 Blue | Diff headers | `@@ -10,5 +10,6 @@` |
| 🟡 Yellow | Warnings | `⚠️ Partial fix` |
| ⚪ White | Info | Status text |

## 🏆 Success Indicators

| Emoji | Status | Meaning |
|-------|--------|---------|
| ✅ | Fixed | All bugs resolved, code runs |
| ⚠️ | Partial | Some bugs fixed, issues remain |
| ❌ | Failed | Repair unsuccessful |
| 🐛 | Error | Bug detected |
| 🔧 | Patch | Fix applied |

## 📈 Scoring System

| Event | Points | Impact |
|-------|--------|--------|
| No errors | +100 | Strongly favors working patches |
| Error reduced | +20 | Per error fixed |
| New error | -50 | Heavily penalizes breakage |
| Minimal change | +10 | Rewards small diffs |

## 🔍 Example Scenarios

### Scenario 1: IndexError Fix
```bash
$ python fixgoblin.py list_bug.py --final-report

✅ Status: Fixed
🐛 1 IndexError detected at line 45
🔧 1 patch applied (Score: 120)
📄 Changed 2 lines
```

### Scenario 2: Multiple Bugs
```bash
$ python fixgoblin.py multi_bug.py --final-report --max-iterations 5

✅ Status: Fixed  
🐛 3 errors: SyntaxError, IndexError, NameError
🔧 3 patches applied
🔄 Took 4 iterations
```

### Scenario 3: Already Working
```bash
$ python fixgoblin.py clean_code.py --final-report

✅ Status: Fixed
🐛 No errors detected
🔧 No patches applied
📄 Code unchanged
```

## 💡 Tips & Tricks

### Best Practices
1. **Always use --final-report** for production debugging
2. **Use --log** to track repair history
3. **Set --max-iterations** based on code complexity
4. **Use --quiet** in automated scripts
5. **Review JSON reports** for detailed analysis

### Performance Tips
- Limit iterations for faster results
- Use efficiency mode only when needed
- Review terminal output before checking JSON
- Keep backup files for safety

### Troubleshooting
- If report fails, check file permissions
- Ensure `backend/logs/` directory exists
- Verify Python 3.7+ is installed
- Check for ANSI color support in terminal

## 🔗 Quick Links

- Main entry: `fixgoblin.py`
- Core modules: `backend/core/`
- Test files: `backend/tests/`
- Logs: `backend/logs/`
- Docs: `backend/docs/`

---

**For detailed information, see [FINAL_REPORT.md](FINAL_REPORT.md)**
