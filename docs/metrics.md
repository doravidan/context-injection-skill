# Measuring Context Injection Impact

## Why Measure

Context Injection is a skill, and like any skill, its value must be demonstrated with data. This document provides a framework for measuring the impact of Context Injection on developer productivity and AI output quality.

---

## Core Metrics

### 1. First-Response Accuracy (FRA)

**Definition:** The percentage of AI responses that are usable without correction on the first attempt.

**How to measure:**
- After each AI interaction, mark: ✅ Usable as-is / ⚠️ Needed minor edits / ❌ Needed major rework or restart
- Calculate: `FRA = (✅ count) / (total interactions) × 100`

| Rating | Without CI | With CI | Target |
|--------|-----------|---------|--------|
| Baseline | ~30% | — | — |
| Week 1 | — | ~65% | 60% |
| Week 4 | — | ~85% | 80% |
| Mature | — | ~90% | 85% |

### 2. Time to Useful Output (TTUO)

**Definition:** The time from first prompt to receiving a usable response, including all correction rounds.

**How to measure:**
- Start timer when you begin composing the prompt (including context assembly)
- Stop timer when you have output you can use
- Include context assembly time (be honest — it counts)

| Task Type | Without CI | With CI | Savings |
|-----------|-----------|---------|---------|
| Bug fix | 10-15 min | 3-5 min | 65-70% |
| New feature | 15-25 min | 5-10 min | 55-65% |
| Code review | 8-12 min | 2-4 min | 65-75% |
| Architecture | 20-30 min | 8-15 min | 50-60% |

### 3. Correction Rounds (CR)

**Definition:** The number of follow-up messages needed to get a usable response.

**How to measure:**
- Count messages after the initial prompt that are corrections, clarifications, or "no, I meant..."
- Don't count genuine follow-up tasks (asking for tests after getting the code is a new task, not a correction)

| Without CI | With CI | Target |
|-----------|---------|--------|
| 3-5 rounds | 0-1 rounds | ≤ 1 |

### 4. Context-Setting Overhead (CSO)

**Definition:** The percentage of total interaction time spent explaining context rather than getting work done.

**How to measure:**
- Track time spent on "let me explain..." vs time the AI is producing useful output
- `CSO = (context explanation time) / (total interaction time) × 100`

| Without CI | With CI | Target |
|-----------|---------|--------|
| 50-70% | 10-20% | < 20% |

*Note: With CI, context assembly time counts but is typically faster (structured, often templated) than ad-hoc explanation.*

### 5. AI Suggestion Adoption Rate (ASAR)

**Definition:** The percentage of AI-generated code/suggestions that make it into the final product (committed code, accepted review comments, etc.).

**How to measure:**
- Track whether AI output was used (fully or with minor modifications) or discarded
- `ASAR = (used outputs) / (total outputs) × 100`

| Without CI | With CI | Target |
|-----------|---------|--------|
| 20-30% | 65-80% | > 70% |

---

## Team-Level Metrics

### 6. Developer Satisfaction Score

**How to measure:** Monthly survey (1-10 scale)

Questions:
1. "How productive do you feel when using AI tools?" (1-10)
2. "How often does the AI give you a useful answer on the first try?" (1-10)
3. "How much time do you spend re-explaining context to the AI?" (1-10, inverted)
4. "Would you recommend AI-assisted development to a colleague?" (1-10)

**Target:** Average ≥ 7.5 (up from typical ~4-5 without CI)

### 7. Template Reuse Rate

**Definition:** How often developers use shared context templates vs. writing context from scratch.

**How to measure:**
- Track template usage in the shared context library
- `Reuse Rate = (templated interactions) / (total interactions) × 100`

**Target:** > 60% of interactions use at least one template

### 8. Context Library Growth

**Definition:** The number and quality of context templates maintained by the team.

**How to measure:**
- Count templates in the shared library
- Track last-modified dates (stale templates = risk)
- Track contributions per team member

**Target:** 10+ templates, updated monthly, contributed by 50%+ of team

---

## Measurement Framework

### Daily Tracking (Individual)

Keep a simple log for one week to establish baselines:

```markdown
## AI Interaction Log - [Date]

| # | Task | CI Used? | FRA | TTUO | CR | Notes |
|---|------|----------|-----|------|----|-------|
| 1 | Fix NPE in OrderService | Yes | ✅ | 4 min | 0 | Used code-task template |
| 2 | Explain caching strategy | No | ❌ | 12 min | 3 | Should have provided arch context |
| 3 | Write unit tests | Yes | ⚠️ | 6 min | 1 | Missed one edge case |
```

### Weekly Summary

```markdown
## Week Summary

| Metric | This Week | Last Week | Trend |
|--------|-----------|-----------|-------|
| Total interactions | 28 | 25 | ↗️ |
| FRA (%) | 78% | 65% | ↗️ |
| Avg TTUO | 5.2 min | 8.1 min | ✅ |
| Avg CR | 0.8 | 1.9 | ✅ |
| Templates used | 18/28 | 12/25 | ↗️ |
```

### Monthly Report (Team)

```markdown
## Monthly CI Impact Report - [Month]

### Adoption
- Team members using CI: 8/10 (80%)
- Context library templates: 14 (+3 this month)
- Template reuse rate: 72%

### Productivity
- Avg FRA: 82% (target: 80%) ✅
- Avg TTUO: 4.8 min (target: 5 min) ✅
- Avg CR: 0.6 (target: ≤1) ✅
- Estimated time saved: 32 hours/month (team total)

### Satisfaction
- Average score: 7.8/10 (up from 4.2 baseline)
- NPS for AI tools: +45 (up from -10 baseline)

### Top Insights
- Code review template most effective (92% FRA)
- Architecture tasks still need improvement (68% FRA)
- New SAP-specific template reduced S/4HANA API integration time by 60%
```

---

## ROI Calculation

### Formula

```
Monthly Time Saved = (Interactions/month) × (TTUO_before - TTUO_after)
Monthly Value = Monthly Time Saved × (Avg Developer Hourly Cost)
Annual Value = Monthly Value × 12
Setup Cost = (Template creation hours) × (Hourly Cost) + Training time
ROI = (Annual Value - Setup Cost) / Setup Cost × 100
```

### Example Calculation

```
Team: 8 developers
Interactions per developer per day: 5
Working days per month: 22

Monthly interactions: 8 × 5 × 22 = 880
TTUO before: 12 minutes average
TTUO after: 4 minutes average
Time saved per interaction: 8 minutes

Monthly time saved: 880 × 8 min = 7,040 min = 117 hours
Developer cost: €80/hour (fully loaded)
Monthly value: 117 × €80 = €9,360

Setup cost (one-time):
- Template creation: 16 hours × €80 = €1,280
- Team training: 8 × 2 hours × €80 = €1,280
- Total setup: €2,560

Annual value: €9,360 × 12 = €112,320
Annual ROI: (€112,320 - €2,560) / €2,560 × 100 = 4,288%
```

---

## A/B Testing Approach

To validate Context Injection impact rigorously:

### Setup
1. Select 10 common development tasks
2. Have each developer attempt 5 tasks WITH CI and 5 WITHOUT (randomized order)
3. Measure FRA, TTUO, and CR for each

### Controls
- Same tasks, same complexity
- Same developer (eliminates skill variance)
- Randomized order (eliminates learning effect)
- Blind evaluation of output quality by reviewer

### Statistical Significance
- With 10 tasks × 8 developers = 80 data points
- Paired t-test on TTUO and CR
- Chi-square test on FRA (categorical)
- Target: p < 0.05 for all metrics

---

## Dashboards

### Individual Dashboard

```
┌──────────────────────────────────────────────┐
│  My Context Injection Stats (This Week)       │
├──────────────────────────────────────────────┤
│                                               │
│  FRA:  ████████████████████░░  82%           │
│  TTUO: ████████░░░░░░░░░░░░░  4.2 min avg   │
│  CR:   ██░░░░░░░░░░░░░░░░░░░  0.7 avg       │
│                                               │
│  Top Template:  code-review.md (used 6x)     │
│  Biggest Win:   Jenkins debug (1 min, FRA ✅) │
│  Needs Work:    Architecture tasks (2 misses) │
│                                               │
└──────────────────────────────────────────────┘
```

### Team Dashboard

```
┌──────────────────────────────────────────────┐
│  Team CI Impact (February 2026)               │
├──────────────────────────────────────────────┤
│                                               │
│  🕐 Time Saved:     117 hours                │
│  💰 Value Created:  €9,360                   │
│  📈 FRA Trend:      65% → 82% (+26%)        │
│  😊 Satisfaction:   4.2 → 7.8 (+86%)        │
│                                               │
│  Template Leaderboard:                        │
│  1. code-task.md       (142 uses)            │
│  2. sap-context.md     (89 uses)             │
│  3. code-review.md     (76 uses)             │
│                                               │
└──────────────────────────────────────────────┘
```

---

## Getting Started with Measurement

1. **Day 1:** Start logging AI interactions (just FRA and TTUO)
2. **Week 1:** Establish baseline without CI
3. **Week 2:** Introduce templates, continue logging
4. **Week 4:** Calculate first comparison metrics
5. **Month 2:** Share team-level results
6. **Month 3:** Calculate ROI, present to management

---

*For the theory, see [How It Works](how-it-works.md).*
*For practical tips, see [Best Practices](best-practices.md).*
