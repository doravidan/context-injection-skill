# ❌ Demo: Without Context Injection

> This demonstrates what happens when you ask an AI for help without providing relevant context.

---

## The Task

A developer needs to add input validation to a REST endpoint in their SAP BTP application.

---

## The Prompt

> Add input validation to my create user endpoint

---

## The AI Response

Sure! Here's how to add input validation to a create user endpoint:

```javascript
app.post('/users', (req, res) => {
    const { name, email, age } = req.body;
    
    // Validation
    if (!name || name.length < 2) {
        return res.status(400).json({ error: 'Name must be at least 2 characters' });
    }
    
    if (!email || !email.includes('@')) {
        return res.status(400).json({ error: 'Valid email is required' });
    }
    
    if (age && (age < 0 || age > 150)) {
        return res.status(400).json({ error: 'Age must be between 0 and 150' });
    }
    
    // Create user
    const user = { id: Date.now(), name, email, age };
    users.push(user);
    
    res.status(201).json(user);
});
```

You might also want to use a validation library like `express-validator` or `joi` for more robust validation.

---

## What Went Wrong

| Issue | Description |
|-------|-------------|
| **Wrong framework** | Used Express.js — the project uses SAP CAP |
| **Wrong validation approach** | Manual validation instead of CDS annotations + `@mandatory` |
| **No SAP patterns** | Ignored XSUAA, CDS service handlers, OData conventions |
| **Wrong error format** | Plain JSON instead of OData error response format |
| **No authorization** | Missing `@requires` annotation and role checks |
| **Wrong entity model** | Made up fields (age?) instead of using actual CDS model |
| **In-memory storage** | `users.push(user)` instead of SAP HANA persistence |
| **No type safety** | No TypeScript, no CDS types |

---

## The Developer's Experience

```
Time: 0:00  → Sent prompt
Time: 0:15  → Received response
Time: 0:20  → "This is Express, we use CAP..."
Time: 1:00  → Rephrased: "We use SAP CAP with CDS..."
Time: 1:30  → Got slightly better answer, but wrong handler pattern
Time: 3:00  → "No, we use class-based handlers, like this..."
Time: 4:00  → Pasted existing code as example
Time: 5:30  → "Also need XSUAA auth..."
Time: 7:00  → "Error format should be OData..."
Time: 9:00  → Finally got something usable
Time: 12:00 → Fixed remaining issues manually

Total time: 12 minutes
Usable on first try: NO
Rounds of correction: 5
Developer frustration: HIGH 😤
```

---

## Root Cause Analysis

The AI had no way to know:

1. ❓ What framework the project uses (Express? Hapi? CAP? Fastify?)
2. ❓ What the actual data model looks like
3. ❓ What validation patterns the team follows
4. ❓ What authorization system is in place
5. ❓ What error format the API uses
6. ❓ What the existing code patterns look like

**Without this information, the AI made the statistically most common assumptions** — which happened to be wrong on every dimension.

---

## The Fix

See [with-context.md](with-context.md) for the same task done correctly with Context Injection.

---

> *"Garbage in, garbage out" isn't just about data — it's about context.*
