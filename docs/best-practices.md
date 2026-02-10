# Best Practices for Context Injection

## The Golden Rules

### 1. Context Before Task, Always

Place all context **before** your request. The model reads sequentially — context that comes after the task doesn't influence the initial response direction.

```markdown
✅ Correct Order:
[Context] → [Task] → [Output Format]

❌ Wrong Order:
[Task] → [Context] → "Oh, I should mention..."
```

### 2. Specific Over General

The more specific your context, the more specific (and useful) the output.

```markdown
❌ "We use Java"
✅ "Java 17, Spring Boot 3.2, Maven, JUnit 5 + Mockito"

❌ "Follow our coding standards"
✅ "Constructor injection only, no Lombok, Javadoc on public methods"
```

### 3. Code Over Descriptions

Include actual code, not descriptions of code. The AI can read code perfectly — it's what it was trained on.

```markdown
❌ "We have a service that handles user creation with validation"
✅ [paste UserService.java — the actual file]
```

### 4. Constraints Are Context Too

What the AI should NOT do is as important as what it should do.

```markdown
## Constraints
- Do NOT add new dependencies
- Do NOT modify the database schema
- Do NOT use deprecated APIs
- Must maintain backward compatibility with v2 clients
```

### 5. Show, Don't Tell

Include an example of what "good" looks like from your codebase. Pattern matching is the AI's strongest capability.

```markdown
## Reference Pattern
Here's how we implemented the OrderService (follow this exact pattern):
[paste OrderService.java]

## Task
Now implement the ShippingService following the same pattern.
```

---

## Practical Tips

### Building a Context Library

Create a folder of reusable context blocks:

```
.ai-context/
├── project-overview.md       # Stack, architecture, team
├── coding-standards.md       # Conventions and rules
├── auth-context.md           # XSUAA, roles, permissions
├── api-conventions.md        # REST/OData patterns
├── testing-standards.md      # Test patterns and tools
├── sap-specifics.md          # SAP BTP, CAP, HANA context
└── error-handling.md         # Error patterns and formats
```

**Usage:** Copy-paste the relevant blocks into your prompt. Most tasks need 2-3 blocks.

### The 30-Second Rule

If assembling context takes more than 30 seconds, you probably need a template. Create one.

If it takes more than 2 minutes, you're probably including too much. Trim to essentials.

### Context Freshness

Stale context is worse than no context — it leads to confidently wrong answers.

| Context Type | Refresh Frequency |
|-------------|-------------------|
| Stack/architecture | When it changes (quarterly) |
| Coding standards | When standards update |
| Relevant code | Every time (paste current version) |
| Error logs | Always paste fresh |
| Configuration | When config changes |

### Progressive Disclosure

For complex tasks, build context across messages instead of one massive block:

```
Message 1: "Here's our project context: [overview]. Does this make sense?"
Message 2: "Now here's the specific module: [code]. And the issue: [error]"
Message 3: "Given all that, [specific task]"
```

This works well when the context would exceed comfortable reading length.

---

## Common Mistakes and Fixes

### Mistake 1: The Kitchen Sink

**Problem:** Pasting an entire file (500+ lines) when only 20 lines are relevant.

**Fix:** Extract the relevant section. Use `// ... rest of file` to indicate omissions.

```java
// ... imports and class declaration

// RELEVANT METHOD:
public Order calculateTotal(Order order) {
    BigDecimal total = order.getLines().stream()
        .map(OrderLine::getAmount)
        .reduce(BigDecimal.ZERO, BigDecimal::add);
    order.setTotal(total);
    return order;
}

// ... rest of OrderService
```

### Mistake 2: Forgetting the "Why"

**Problem:** Including what the code does but not why the task exists.

**Fix:** Add one line of business context.

```markdown
## Background
Customer complaints about wrong totals when applying multiple 
discount codes (JIRA: SHOP-4521, P1).
```

### Mistake 3: Ambiguous Standards

**Problem:** "Follow best practices" — whose best practices?

**Fix:** State the specific standard and give an example.

```markdown
## Standards
- Error handling: Use `req.error(statusCode, message, target)` pattern
- Example: `req.error(400, 'Email is required', 'email')`
- Multiple errors accumulate (don't throw on first error)
```

### Mistake 4: Missing Version Numbers

**Problem:** "We use Spring Boot" — which version? The API changed significantly between 2.x and 3.x.

**Fix:** Always include version numbers for frameworks and key dependencies.

```markdown
- Spring Boot 3.2.3 (NOT 2.x — we migrated last quarter)
- Java 17 (not 21 — we haven't upgraded yet)
- PostgreSQL 15.4
```

### Mistake 5: No Output Format Specification

**Problem:** The AI gives a long explanation when you wanted code, or code when you wanted an explanation.

**Fix:** Explicitly state what you want back.

```markdown
## Expected Output
- Updated Java method (just the method, not the whole class)
- JUnit test for the happy path
- One sentence explaining the approach
```

---

## SAP-Specific Best Practices

### Always Specify SAP Versions and Services

SAP's ecosystem has many overlapping services. Be explicit:

```markdown
❌ "We use SAP authentication"
✅ "SAP XSUAA (service plan: application) with role collections: Employee, Manager, Admin"

❌ "We use SAP database"
✅ "SAP HANA Cloud (HDI containers, CDS-managed schema)"

❌ "We use SAP messaging"
✅ "SAP Event Mesh (enterprise-messaging, 'default' plan)"
```

### Include CDS Models

For CAP projects, the CDS model is the most important context:

```markdown
## CDS Model
```cds
namespace sap.myapp;
entity MyEntity : cuid, managed {
    // ... actual CDS definition
}
```
```

The AI can infer entity names, types, associations, and annotations from CDS — this is often all it needs.

### Reference SAP Documentation Patterns

When SAP has an official pattern, mention it:

```markdown
Follow the SAP CAP best practice for custom handlers:
- Class-based service implementation (extends cds.ApplicationService)
- Use this.before/on/after for event hooks
- Use cds.log() for structured logging
- Ref: https://cap.cloud.sap/docs/node.js/core-services
```

### Clean Core Awareness

For S/4HANA-related work, explicitly state Clean Core compliance:

```markdown
## SAP Clean Core
- NO modifications to SAP standard objects
- Side-by-side extension on BTP only
- Use released APIs (check SAP API Business Hub)
- Key User Extensibility where applicable
```

---

## Team Adoption Checklist

When rolling out Context Injection to your team:

- [ ] Create a shared context library (`.ai-context/` directory)
- [ ] Write context templates for your top 5 task types
- [ ] Add context assembly to your definition of "ready" for AI-assisted tasks
- [ ] Share effective prompts in a team channel
- [ ] Review and update context blocks monthly
- [ ] Measure before/after metrics (see [Metrics](metrics.md))

---

## Quick Reference Card

```
╔══════════════════════════════════════════════════╗
║          Context Injection Quick Reference        ║
╠══════════════════════════════════════════════════╣
║                                                   ║
║  1. WHAT → Project, stack, module                 ║
║  2. WHERE → Relevant files (paste actual code)    ║
║  3. HOW → Team conventions and patterns           ║
║  4. WHY → Business context, ticket, constraint    ║
║  5. NOT → What to avoid, constraints              ║
║  6. DONE → Expected output format                 ║
║                                                   ║
║  Order: Context → Task → Output Format            ║
║  Size: Minimum needed + one safety layer          ║
║  Rule: Specific > General, Code > Description     ║
║                                                   ║
╚══════════════════════════════════════════════════╝
```

---

*For theory, see [How It Works](how-it-works.md).*
*For measurement, see [Metrics](metrics.md).*
