# Quick Reference: Testing & Logging

## 🚀 Most Common Commands

```bash
# Default development workflow
hatch run fast:test                    # All tests, fast environment (RECOMMENDED)

# Quick feedback during TDD  
hatch run fast:fast-only              # Skip slow tests

# Change log level for debugging
python set-test-log-level.py DEBUG    # Detailed output
.\set-log-level.ps1 INFO              # Windows: Normal output
```

## 📊 Log Levels at a Glance

| Level | When to Use | What You See |
|-------|-------------|--------------|
| `DEBUG` | 🐛 **Troubleshooting** | SQL queries, internal state, all details |
| `INFO` | 📋 **Default dev** | Test progress, basic operations |
| `WARNING` | ⚡ **CI/CD, fast runs** | Only warnings and errors |
| `ERROR` | 🚨 **Production** | Only error messages |
| `CRITICAL` | 💥 **Monitoring** | Only critical failures |

## 🛠️ One-Liner Setups

```powershell
# PowerShell: Debug a failing test
$env:REVIEWPOINT_TEST_LOG_LEVEL='DEBUG'; hatch run fast:test tests/test_specific.py

# PowerShell: Quiet CI run
$env:REVIEWPOINT_TEST_LOG_LEVEL='WARNING'; hatch run fast:test

# PowerShell: Reset to default
$env:REVIEWPOINT_TEST_LOG_LEVEL='INFO'; hatch run fast:test
```

```bash
# Bash: Debug a failing test
REVIEWPOINT_TEST_LOG_LEVEL=DEBUG hatch run fast:test tests/test_specific.py

# Bash: Quiet CI run  
REVIEWPOINT_TEST_LOG_LEVEL=WARNING hatch run fast:test

# Bash: Reset to default
REVIEWPOINT_TEST_LOG_LEVEL=INFO hatch run fast:test
```

## 📝 Helper Scripts

| Script | Purpose | Example |
|--------|---------|---------|
| `python set-test-log-level.py` | Cross-platform log config | `python set-test-log-level.py DEBUG` |
| `.\set-log-level.ps1` | Windows PowerShell (colored) | `.\set-log-level.ps1 WARNING` |
| No args | Show current config | `python set-test-log-level.py` |

## 🎯 Pro Tips

- **Start with INFO**: Good balance for daily development
- **Use DEBUG when stuck**: Shows SQL and detailed traces  
- **Use WARNING in CI**: Faster, less noisy output
- **Check log files**: `tests/test_debug.log` always has full DEBUG logs
- **Environment persists**: Set once, applies to all test runs in that session

---

📖 **Full docs:** [TESTING.md](TESTING.md) | [TEST_LOGGING.md](TEST_LOGGING.md)
