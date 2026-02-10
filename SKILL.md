# Context Injection — Complete Skill Guide

## Overview

**Context Injection** is the practice of systematically assembling and prepending relevant information to AI prompts, enabling the AI to produce accurate, project-specific output on the first attempt.

This document provides the complete, step-by-step process for mastering Context Injection.

---

## Table of Contents

1. [Core Concept](#core-concept)
2. [The Process](#the-process)
3. [Context Sources](#context-sources)
4. [Context Assembly](#context-assembly)
5. [Injection Patterns](#injection-patterns)
6. [Templates](#templates)
7. [When to Use What](#when-to-use-what)
8. [Advanced Techniques](#advanced-techniques)
9. [Anti-Patterns](#anti-patterns)

---

## Core Concept

AI language models generate responses token-by-token, where each token is influenced by all preceding tokens. **Context placed early in the prompt shapes every subsequent token the model generates.**

This means:
- Context that appears *before* the task biases the entire response toward relevance
- More specific context produces more specific (and accurate) output
- Structured context is processed more reliably than unstructured narrative

**The Formula:**

```
Effective Prompt = Relevant Context + Clear Task + Output Constraints
```

---

## The Process

### Step 1: Define the Task

Before gathering context, clearly articulate what you need. A vague task leads to vague context selection.

| ❌ Vague | ✅ Specific |
|----------|-----------|
| "Help with the API" | "Add pagination to the GET /orders endpoint" |
| "Fix the bug" | "Fix the NPE in OrderService.calculateTotal() when discount is null" |
| "Review this code" | "Review this PR for security issues in input validation" |

### Step 2: Identify Relevant Context

Ask yourself these questions:

1. **What does the AI need to know about the project?** (stack, architecture, conventions)
2. **What specific code/config is involved?** (files, functions, schemas)
3. **What constraints exist?** (backward compatibility, performance, compliance)
4. **What has been tried before?** (previous approaches, why they failed)
5. **What does "done" look like?** (acceptance criteria, team standards)

### Step 3: Gather Context from Sources

Pull information from the relevant sources (see [Context Sources](#context-sources) below).

**Rule of thumb:** Include the *minimum context needed* for the AI to produce a correct answer. Too little = generic output. Too much = diluted focus.

### Step 4: Assemble the Context Block

Structure your context using one of the [Templates](#templates). Key principles:

- **Structured over narrative** — Use headers, tables, and code blocks
- **Specific over general** — Include actual code, not descriptions of code
- **Constrained over open** — State what the AI should NOT do as well

### Step 5: Inject and Prompt

Place the context block at the beginning of your prompt, followed by the task:

```
[CONTEXT BLOCK]

---

## Task
[Your specific request]

## Expected Output
[What you want back: code, explanation, review, etc.]
```

### Step 6: Evaluate and Iterate

After receiving the response:
- Did the AI use the context correctly?
- Was anything missing that caused a wrong assumption?
- Save effective context blocks as templates for reuse

---

## Context Sources

### Primary Sources

| Source | What to Extract | When to Use | Priority |
|--------|----------------|-------------|----------|
| **Source Code** | Relevant files, interfaces, models | Always for code tasks | 🔴 Critical |
| **Error Output** | Stack traces, logs, error messages | Debugging tasks | 🔴 Critical |
| **Documentation** | READMEs, ADRs, API specs | Architecture & design tasks | 🟡 High |
| **Issue Tracker** | Ticket details, comments, history | Ticket-based work | 🟡 High |
| **Configuration** | Build files, env config, CI/CD | Infrastructure tasks | 🟡 High |
| **Git History** | Recent commits, blame, diff | Understanding changes | 🟢 Medium |
| **Team Standards** | Coding guidelines, review checklists | Code review, new code | 🟢 Medium |
| **Runtime Data** | Metrics, dashboards, APM | Performance tasks | 🟢 Medium |

### SAP-Specific Sources

| Source | What to Extract | Example |
|--------|----------------|---------|
| **CDS Models** | Entity definitions, associations, annotations | `schema.cds`, `service.cds` |
| **SAP API Hub** | API specifications, field descriptions | S/4HANA OData APIs |
| **Authorization** | Auth objects, roles, PFCG data | `@requires`, `@restrict` |
| **Extension Points** | BAdIs, Enhancement Spots, custom logic | BADI implementations |
| **Transaction Codes** | Relevant t-codes, their purpose | SE38, SM37, SLG1 |
| **SAP Notes** | Relevant OSS notes, KBAs | SAP Note 1234567 |

---

## Context Assembly

### Structure

A well-assembled context block follows this hierarchy:

```markdown
## Context

### Project Overview
[One-liner about the project, stack, and domain]

### Architecture
[Relevant architectural context — components, patterns, data flow]

### Relevant Code
[Actual code files or snippets that the AI needs to see]

### Standards & Constraints
[Team conventions, non-functional requirements, limitations]

### Background
[Why this task exists — ticket, incident, decision]

---

## Task
[What you need the AI to do]

## Output Format
[How you want the response structured]
```

### Sizing Guide

| Task Complexity | Context Size | Example |
|----------------|-------------|---------|
| Simple (fix typo, rename) | 5-15 lines | File + convention |
| Medium (implement feature) | 30-80 lines | Files + architecture + standards |
| Complex (design decision) | 80-200 lines | Full architectural context + ADRs |
| Critical (production issue) | 50-150 lines | Logs + code + runbook + timeline |

---

## Injection Patterns

### Pattern 1: Inline Context

Best for simple, one-off tasks.

```
Given this Java class:
[paste class]

And our team convention of using constructor injection (not @Autowired):

Add a new dependency on PricingService to this class.
```

### Pattern 2: Structured Block

Best for medium-complexity tasks. Uses clear sections.

```markdown
## Context
**Project:** E-commerce checkout service
**Stack:** Java 17, Spring Boot 3.2, PostgreSQL
**Pattern:** Hexagonal architecture (ports & adapters)

**Existing code:**
[paste relevant interface and implementation]

## Task
Implement the new PaymentPort for Stripe integration

## Constraints
- Follow existing port/adapter pattern
- Include unit tests with Mockito
- No Lombok (team standard)
```

### Pattern 3: Persona Injection

Set the AI's role to match the expertise needed.

```markdown
You are a senior SAP BTP developer with deep expertise in CAP (Node.js) 
and SAP HANA Cloud. You follow SAP's Clean Core principles and prefer 
side-by-side extensions over in-app modifications.

## Context
[project details]

## Task
[specific request]
```

### Pattern 4: Multi-Source Aggregation

For complex tasks, pull context from multiple sources into one block.

```markdown
## Context

### From JIRA (PROJ-1234)
[ticket description + acceptance criteria]

### From Codebase
[relevant source files]

### From Architecture Decision Records
[relevant ADR excerpt]

### From CI/CD
[relevant pipeline config or recent failure]

### From Team Standards
[relevant coding guidelines]

## Task
[request that needs all this context]
```

---

## Templates

Ready-to-use templates are available in the [`templates/`](templates/) directory:

| Template | Use Case | Complexity |
|----------|----------|------------|
| [Basic Context](templates/basic-context-template.md) | Quick tasks, simple questions | Low |
| [Code Task](templates/code-task-template.md) | Implementation, debugging, refactoring | Medium |
| [Enterprise Context](templates/enterprise-context-template.md) | Cross-cutting, SAP-specific, compliance | High |

---

## When to Use What

| Situation | Pattern | Context Size | Template |
|-----------|---------|-------------|----------|
| Quick question about code | Inline | Small | Basic |
| Bug fix | Structured Block | Medium | Code Task |
| New feature implementation | Structured Block | Medium-Large | Code Task |
| Code review | Multi-Source | Medium | Code Task |
| Architecture decision | Multi-Source + Persona | Large | Enterprise |
| Production incident | Structured Block | Medium-Large | Enterprise |
| SAP-specific development | Persona + Multi-Source | Large | Enterprise |

---

## Advanced Techniques

### 1. Context Layering

Build context progressively across a conversation:

```
Message 1: [Project context] + "Explain the current architecture"
Message 2: [AI's understanding confirmed] + "Now, given this ADR..." + [task]
Message 3: [Previous output] + "Refine based on these test results..." + [data]
```

### 2. Negative Context

Tell the AI what NOT to do (often as important as what to do):

```markdown
## Constraints
- Do NOT use @Autowired (we use constructor injection)
- Do NOT suggest database schema changes (frozen for this release)
- Do NOT use Java records (team hasn't adopted yet)
- Do NOT import any new dependencies
```

### 3. Example-Driven Context

Show the AI what "good" looks like by including an example from your codebase:

```markdown
## Reference Implementation
Here's how we implemented the UserService (follow this pattern exactly):
[paste UserService.java]

## Task
Now implement ProductService following the same pattern.
```

### 4. Context Caching

For repeated tasks, maintain a **context library** — pre-written context blocks for common scenarios:

```
contexts/
├── project-overview.md       # General project context
├── auth-context.md           # Authentication system context
├── api-conventions.md        # API design standards
├── testing-standards.md      # Testing conventions
└── sap-integration.md        # SAP-specific context
```

### 5. Dynamic Context Generation

Use scripts to auto-generate context from your environment:

```bash
# Generate context from git
echo "## Recent Changes"
git log --oneline -10

echo "## Modified Files"
git diff --name-only HEAD~3

echo "## Current Branch"
git branch --show-current
```

---

## Anti-Patterns

### ❌ The Info Dump
Pasting entire files or repos without filtering. The AI drowns in noise.

**Fix:** Extract only the relevant sections. Use `...` to indicate omitted code.

### ❌ The Assumption
Assuming the AI knows your project, stack, or conventions because "it's popular."

**Fix:** Always state your stack, version, and key conventions explicitly.

### ❌ The Afterthought
Adding context after the task: "Oh and by the way, we use Spring Boot 2.x not 3.x."

**Fix:** Always place context BEFORE the task.

### ❌ The Novel
Writing paragraphs of prose when structured data would be clearer.

**Fix:** Use tables, bullet points, and code blocks. Structure > prose.

### ❌ The One-Shot
Never refining or reusing context blocks.

**Fix:** Save effective context blocks as templates. Iterate based on output quality.

---

## Next Steps

1. **Start small:** Use the [Basic Context Template](templates/basic-context-template.md) on your next AI interaction
2. **Compare results:** Try the same task with and without context (see [demo/](demo/))
3. **Build your library:** Create context blocks for your most common tasks
4. **Share with your team:** Context templates are a team asset — share what works
5. **Measure impact:** Track the [metrics](docs/metrics.md) that matter

---

*For the theory behind why this works, see [How It Works](docs/how-it-works.md).*
*For tips and pitfalls, see [Best Practices](docs/best-practices.md).*
*For measurement and ROI, see [Metrics](docs/metrics.md).*
