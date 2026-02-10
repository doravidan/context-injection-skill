#!/usr/bin/env python3
"""
Context Injection Skill - Test Runner
=====================================
Runs the same task with and without rich context, comparing the quality of
AI responses. Uses the Anthropic API directly.

Usage:
    python3 test-runner.py --all                          # Run all tests
    python3 test-runner.py --test test_code_fix            # Run one test
    python3 test-runner.py --all --output results/         # Save results
    python3 test-runner.py --all --evaluate                # Auto-evaluate with LLM
"""

import anthropic
import json
import time
import argparse
import os
import sys
import glob
from datetime import datetime
from pathlib import Path

# ─── Configuration ──────────────────────────────────────────────────────────

MODEL = "claude-3-5-haiku-20241022"
MAX_TOKENS = 1500
EVAL_MODEL = "claude-3-5-haiku-20241022"

# ─── Colors for terminal output ─────────────────────────────────────────────

class C:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    END = "\033[0m"

def colored(text, color):
    return f"{color}{text}{C.END}"

# ─── Core Test Runner ───────────────────────────────────────────────────────

def load_test_case(path: str) -> dict:
    """Load a test case from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def run_single_prompt(client: anthropic.Anthropic, prompt: str) -> dict:
    """Send a single prompt to the API and return response + metadata."""
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = time.time() - start

    text = response.content[0].text if response.content else ""
    return {
        "text": text,
        "time_seconds": round(elapsed, 2),
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": MODEL,
    }


def evaluate_criteria(
    client: anthropic.Anthropic,
    response_text: str,
    criteria: list[str],
    test_name: str,
    mode: str,
) -> dict:
    """Use LLM to evaluate how well a response meets the criteria."""
    criteria_list = "\n".join(f"  {i+1}. {c}" for i, c in enumerate(criteria))

    eval_prompt = f"""You are an objective evaluator. Assess how well the following AI response meets each criterion.

## Test: {test_name} ({mode})

## Response to evaluate:
{response_text}

## Criteria:
{criteria_list}

For EACH criterion, respond with:
- "PASS" if the response clearly addresses it
- "PARTIAL" if it somewhat addresses it
- "FAIL" if it doesn't address it at all
- Brief explanation (1 sentence)

Then give an overall score from 0-10.

Respond in this exact JSON format:
{{
  "criteria_results": [
    {{"criterion": "...", "result": "PASS|PARTIAL|FAIL", "explanation": "..."}},
    ...
  ],
  "overall_score": 7,
  "summary": "One sentence overall assessment"
}}"""

    response = client.messages.create(
        model=EVAL_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": eval_prompt}],
    )

    text = response.content[0].text if response.content else "{}"
    # Extract JSON from response (handle markdown code blocks)
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"error": "Failed to parse evaluation", "raw": text}


def run_test(client: anthropic.Anthropic, test_case: dict, auto_evaluate: bool = False) -> dict:
    """Run a complete test: without context, with context, compare."""
    name = test_case["name"]
    print(f"\n{'='*70}")
    print(colored(f"  TEST: {name}", C.BOLD + C.HEADER))
    print(f"{'='*70}")

    # ── Run WITHOUT context ──────────────────────────────────────────────
    print(colored("\n▶ Running WITHOUT context...", C.YELLOW))
    without = run_single_prompt(client, test_case["without_context"])
    print(colored(f"  ✓ Done ({without['time_seconds']}s, {without['input_tokens']}→{without['output_tokens']} tokens)", C.DIM))

    # ── Run WITH context ─────────────────────────────────────────────────
    print(colored("\n▶ Running WITH context...", C.CYAN))
    with_ctx = run_single_prompt(client, test_case["with_context"])
    print(colored(f"  ✓ Done ({with_ctx['time_seconds']}s, {with_ctx['input_tokens']}→{with_ctx['output_tokens']} tokens)", C.DIM))

    result = {
        "name": name,
        "task": test_case["task"],
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "without_context": without,
        "with_context": with_ctx,
        "evaluation_criteria": test_case.get("evaluation_criteria", []),
        "prompt_size_ratio": round(
            len(test_case["with_context"]) / max(len(test_case["without_context"]), 1), 1
        ),
    }

    # ── Auto-evaluate if requested ───────────────────────────────────────
    if auto_evaluate and test_case.get("evaluation_criteria"):
        print(colored("\n▶ Evaluating responses against criteria...", C.BLUE))
        criteria = test_case["evaluation_criteria"]

        eval_without = evaluate_criteria(client, without["text"], criteria, name, "WITHOUT context")
        eval_with = evaluate_criteria(client, with_ctx["text"], criteria, name, "WITH context")

        result["evaluation"] = {
            "without_context": eval_without,
            "with_context": eval_with,
        }

        score_without = eval_without.get("overall_score", "?")
        score_with = eval_with.get("overall_score", "?")
        print(colored(f"  Score WITHOUT context: {score_without}/10", C.YELLOW))
        print(colored(f"  Score WITH context:    {score_with}/10", C.GREEN))

    # ── Print comparison ─────────────────────────────────────────────────
    print_comparison(result)

    return result


def print_comparison(result: dict):
    """Print a side-by-side comparison of results."""
    without = result["without_context"]
    with_ctx = result["with_context"]

    print(f"\n{'─'*70}")
    print(colored("  COMPARISON", C.BOLD))
    print(f"{'─'*70}")

    # Metrics table
    print(f"\n  {'Metric':<25} {'Without Context':<20} {'With Context':<20}")
    print(f"  {'─'*65}")
    print(f"  {'Response time':<25} {without['time_seconds']:<20}s {with_ctx['time_seconds']:<20}s")
    print(f"  {'Input tokens':<25} {without['input_tokens']:<20} {with_ctx['input_tokens']:<20}")
    print(f"  {'Output tokens':<25} {without['output_tokens']:<20} {with_ctx['output_tokens']:<20}")
    print(f"  {'Response length':<25} {len(without['text']):<20} {len(with_ctx['text']):<20}")
    print(f"  {'Prompt size ratio':<25} {'1x':<20} {result['prompt_size_ratio']}x")

    # Criteria check
    if result.get("evaluation"):
        eval_w = result["evaluation"]["without_context"]
        eval_c = result["evaluation"]["with_context"]

        if "criteria_results" in eval_w and "criteria_results" in eval_c:
            print(f"\n  {'Criterion':<45} {'Without':<12} {'With':<12}")
            print(f"  {'─'*65}")
            for cw, cc in zip(eval_w["criteria_results"], eval_c["criteria_results"]):
                criterion = cw["criterion"][:42]
                r_w = cw["result"]
                r_c = cc["result"]
                color_w = C.GREEN if r_w == "PASS" else (C.YELLOW if r_w == "PARTIAL" else C.RED)
                color_c = C.GREEN if r_c == "PASS" else (C.YELLOW if r_c == "PARTIAL" else C.RED)
                print(f"  {criterion:<45} {colored(r_w, color_w):<23} {colored(r_c, color_c):<23}")

            score_w = eval_w.get("overall_score", "?")
            score_c = eval_c.get("overall_score", "?")
            print(f"\n  {'OVERALL SCORE':<45} {score_w}/10{'':>8} {score_c}/10")

            if isinstance(score_w, (int, float)) and isinstance(score_c, (int, float)):
                delta = score_c - score_w
                sign = "+" if delta > 0 else ""
                color = C.GREEN if delta > 0 else (C.RED if delta < 0 else C.DIM)
                print(colored(f"\n  Context injection improvement: {sign}{delta} points", color))

    # Response previews
    preview_len = 300
    print(colored(f"\n  ┌─ Response WITHOUT context (first {preview_len} chars):", C.YELLOW))
    for line in without["text"][:preview_len].split("\n"):
        print(colored(f"  │ {line}", C.DIM))
    if len(without["text"]) > preview_len:
        print(colored(f"  │ ... ({len(without['text']) - preview_len} more chars)", C.DIM))

    print(colored(f"\n  ┌─ Response WITH context (first {preview_len} chars):", C.GREEN))
    for line in with_ctx["text"][:preview_len].split("\n"):
        print(colored(f"  │ {line}", C.DIM))
    if len(with_ctx["text"]) > preview_len:
        print(colored(f"  │ ... ({len(with_ctx['text']) - preview_len} more chars)", C.DIM))


def print_summary(all_results: list[dict]):
    """Print overall summary across all tests."""
    print(f"\n{'='*70}")
    print(colored("  OVERALL SUMMARY", C.BOLD + C.HEADER))
    print(f"{'='*70}\n")

    print(f"  Tests run: {len(all_results)}")
    print(f"  Model: {MODEL}")
    print(f"  Timestamp: {datetime.now().isoformat()}\n")

    has_eval = any(r.get("evaluation") for r in all_results)

    print(f"  {'Test':<35} {'Time Δ':<12} {'Tokens Δ':<12}", end="")
    if has_eval:
        print(f" {'Score Δ':<12}", end="")
    print()
    print(f"  {'─'*70}")

    total_score_without = 0
    total_score_with = 0
    scored_count = 0

    for r in all_results:
        name = r["name"][:32]
        time_delta = r["with_context"]["time_seconds"] - r["without_context"]["time_seconds"]
        token_delta = (
            r["with_context"]["output_tokens"] - r["without_context"]["output_tokens"]
        )
        time_str = f"{'+' if time_delta > 0 else ''}{time_delta:.1f}s"
        token_str = f"{'+' if token_delta > 0 else ''}{token_delta}"

        print(f"  {name:<35} {time_str:<12} {token_str:<12}", end="")

        if has_eval and r.get("evaluation"):
            ew = r["evaluation"]["without_context"]
            ec = r["evaluation"]["with_context"]
            sw = ew.get("overall_score", 0)
            sc = ec.get("overall_score", 0)
            if isinstance(sw, (int, float)) and isinstance(sc, (int, float)):
                delta = sc - sw
                color = C.GREEN if delta > 0 else (C.RED if delta < 0 else C.DIM)
                print(colored(f" {'+' if delta > 0 else ''}{delta}", color), end="")
                total_score_without += sw
                total_score_with += sc
                scored_count += 1
        print()

    if scored_count > 0:
        avg_without = total_score_without / scored_count
        avg_with = total_score_with / scored_count
        avg_delta = avg_with - avg_without
        color = C.GREEN if avg_delta > 0 else C.RED
        print(f"\n  {'─'*70}")
        print(f"  Average score WITHOUT context: {avg_without:.1f}/10")
        print(f"  Average score WITH context:    {avg_with:.1f}/10")
        print(colored(f"  Average improvement:           {'+' if avg_delta > 0 else ''}{avg_delta:.1f} points", color))


def save_results(results: list[dict], output_dir: str):
    """Save results to JSON files."""
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save individual results
    for r in results:
        slug = r["name"].lower().replace(" ", "_").replace("-", "_")[:40]
        path = os.path.join(output_dir, f"{timestamp}_{slug}.json")
        with open(path, "w") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
        print(colored(f"  Saved: {path}", C.DIM))

    # Save combined report
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "test_count": len(results),
        "results": results,
    }
    report_path = os.path.join(output_dir, f"{timestamp}_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(colored(f"  Saved report: {report_path}", C.GREEN))


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    global MODEL  # Declare global at start of function
    parser = argparse.ArgumentParser(
        description="Context Injection Skill — Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 test-runner.py --all
  python3 test-runner.py --all --evaluate --output results/
  python3 test-runner.py --test test_code_fix
        """,
    )
    parser.add_argument("--all", action="store_true", help="Run all test cases")
    parser.add_argument("--test", type=str, help="Run a specific test (name without .json)")
    parser.add_argument("--output", type=str, help="Directory to save results")
    parser.add_argument("--evaluate", action="store_true", help="Auto-evaluate with LLM")
    parser.add_argument("--model", type=str, default=MODEL, help=f"Model to use (default: {MODEL})")
    args = parser.parse_args()

    if not args.all and not args.test:
        parser.print_help()
        sys.exit(1)

    # Allow model override
    if args.model:
        MODEL = args.model

    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(colored("Error: ANTHROPIC_API_KEY environment variable not set.", C.RED))
        sys.exit(1)

    client = anthropic.Anthropic()

    # Find test cases directory
    script_dir = Path(__file__).parent
    test_cases_dir = script_dir / "test-cases"

    if not test_cases_dir.exists():
        print(colored(f"Error: test-cases directory not found at {test_cases_dir}", C.RED))
        sys.exit(1)

    # Load test cases
    if args.all:
        test_files = sorted(test_cases_dir.glob("*.json"))
    else:
        test_file = test_cases_dir / f"{args.test}.json"
        if not test_file.exists():
            print(colored(f"Error: Test case not found: {test_file}", C.RED))
            available = [f.stem for f in test_cases_dir.glob("*.json")]
            print(f"Available tests: {', '.join(available)}")
            sys.exit(1)
        test_files = [test_file]

    print(colored(f"\n🧪 Context Injection Skill — Test Runner", C.BOLD + C.HEADER))
    print(colored(f"   Model: {MODEL}", C.DIM))
    print(colored(f"   Tests: {len(test_files)}", C.DIM))
    print(colored(f"   Evaluate: {'Yes' if args.evaluate else 'No'}", C.DIM))
    print(colored(f"   Time: {datetime.now().isoformat()}", C.DIM))

    # Run tests
    all_results = []
    for test_file in test_files:
        test_case = load_test_case(str(test_file))
        result = run_test(client, test_case, auto_evaluate=args.evaluate)
        all_results.append(result)

    # Summary
    if len(all_results) > 1:
        print_summary(all_results)

    # Save results
    if args.output:
        print(colored(f"\n💾 Saving results to {args.output}/", C.BOLD))
        save_results(all_results, args.output)

    print(colored("\n✅ Done!\n", C.GREEN + C.BOLD))


if __name__ == "__main__":
    main()
