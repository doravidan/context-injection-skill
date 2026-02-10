# Basic Context Template

> Use this template for quick, focused tasks where minimal context is sufficient.

---

## Template

```markdown
## Context

**Project:** [Project name]
**Stack:** [Language, framework, key dependencies]
**File:** [Relevant file path]

**Relevant Code:**
```
[paste the specific code the AI needs to see]
```

**Constraint:** [Any key limitation or standard to follow]

---

## Task
[Your specific request — one clear action]

## Expected Output
[What format you want: code, explanation, list, etc.]
```

---

## When to Use

- Quick bug fixes (single file)
- Simple questions about specific code
- Small refactoring tasks
- Generating boilerplate that matches a pattern

## When NOT to Use

- Multi-file changes → use [Code Task Template](code-task-template.md)
- Architecture decisions → use [Enterprise Template](enterprise-context-template.md)
- Tasks requiring team standards or compliance → use Enterprise Template

---

## Example: Filled In

```markdown
## Context

**Project:** User Dashboard (React)
**Stack:** TypeScript, React 18, TanStack Query v5
**File:** `src/hooks/useUsers.ts`

**Relevant Code:**
```typescript
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.get('/users').then(r => r.data),
  });
}
```

**Constraint:** All hooks must include error handling and loading states consistent with our ErrorBoundary pattern.

---

## Task
Add pagination support (offset-based) to the useUsers hook.

## Expected Output
Updated TypeScript hook with pagination parameters and return values.
```

---

## Tips

1. **Be specific about the file** — include the path so the AI knows the context
2. **One constraint is often enough** — state the most important standard
3. **Keep it short** — basic template should be < 20 lines when filled in
4. **Include actual code** — descriptions of code are never as good as the code itself
