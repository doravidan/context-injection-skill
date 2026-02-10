# Context Injection Skill — Test Suite

Empirical tests that demonstrate the value of context injection by running the **same task** with and without rich context, then comparing results.

## Quick Start

```bash
# 1. Set your API key
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Install dependency
pip3 install anthropic

# 3. Run all tests
./run_all_tests.sh

# 4. Run with auto-evaluation (LLM judges responses against criteria)
./run_all_tests.sh --evaluate
```

## Structure

```
tests/
├── test-runner.py          # Main test runner script
├── run_all_tests.sh        # Convenience wrapper
├── README.md               # This file
├── test-cases/             # Test case definitions (JSON)
│   ├── test_code_fix.json
│   ├── test_jira_ticket.json
│   ├── test_code_review.json
│   └── test_architecture.json
└── results/                # Saved test results (gitignored)
```

## Test Cases

| Test | Task | Key Insight |
|------|------|-------------|
| **Code Fix** | Fix NullPointerException | Without context: generic advice. With context: identifies `address.getCity()` as root cause, uses team's Optional standards |
| **Jira Ticket** | Respond to P1 incident | Without context: vague troubleshooting. With context: connects pool exhaustion + Feb 1 deploy + SLA breach |
| **Code Review** | Review caching PR | Without context: surface-level feedback. With context: catches ADR violation, multi-pod staleness, past incident precedent |
| **Architecture** | Design event system | Without context: generic architecture. With context: avoids Kafka (team failed before), stays within $8K budget, fits existing AWS stack |

## Usage

### Run all tests
```bash
python3 test-runner.py --all
```

### Run a specific test
```bash
python3 test-runner.py --test test_code_fix
```

### Run with auto-evaluation
The `--evaluate` flag uses an LLM to score each response against the test's evaluation criteria:
```bash
python3 test-runner.py --all --evaluate --output results/
```

### Use a different model
```bash
python3 test-runner.py --all --model claude-sonnet-4-20250514
```

### Save results
```bash
python3 test-runner.py --all --output results/
```

Results are saved as timestamped JSON files in the output directory.

## How It Works

1. **Load** test case JSON (contains `without_context` and `with_context` prompts)
2. **Run** both prompts against the Anthropic API (same model, same parameters)
3. **Compare** response time, token usage, and response content
4. **Evaluate** (optional) — uses LLM to judge each response against predefined criteria
5. **Report** — prints side-by-side comparison with colored output

## Evaluation Criteria

Each test case defines specific criteria that a good response should meet. These criteria are designed so that responses **with** rich context naturally score higher, because they have the information needed to address the specifics.

Example (Code Fix test):
- ✅ Identifies `address.getCity()` as the null source
- ✅ Uses Optional-based handling per team standards
- ✅ Preserves backward compatibility
- ✅ Doesn't suggest schema changes

## Expected Results

With context injection, responses should:
- **Score 3-5 points higher** on evaluation criteria
- **Be more specific** (mention actual variable names, config values, team standards)
- **Avoid wrong suggestions** (no schema changes, no Kafka, etc.)
- **Reference related context** (past incidents, ADRs, team preferences)

## Cost

Each full test run (4 tests × 2 prompts) costs approximately **$0.02-0.05** with Haiku.
Adding `--evaluate` roughly doubles the cost (extra evaluation prompts).
