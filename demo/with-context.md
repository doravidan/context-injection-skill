# ✅ Demo: With Context Injection

> The same task as [without-context.md](without-context.md), but this time with proper context injection.

---

## The Task

A developer needs to add input validation to a REST endpoint in their SAP BTP application.

---

## The Prompt (with Context Injection)

```markdown
## Context

### Project
- **Name:** Employee Directory Service
- **Stack:** SAP CAP (Node.js 18), CDS 7.5, SAP HANA Cloud
- **Auth:** SAP XSUAA with role collections: Employee, Manager, Admin
- **Environment:** SAP BTP Cloud Foundry (EU10)

### CDS Model (db/schema.cds)
```cds
namespace sap.hr;

using { cuid, managed } from '@sap/cds/common';

entity Employees : cuid, managed {
    firstName   : String(100) @mandatory;
    lastName    : String(100) @mandatory;
    email       : String(200) @mandatory @assert.format: '[^@]+@[^@]+\.[^@]+';
    department  : Association to Departments @mandatory;
    position    : String(100);
    hireDate    : Date        @mandatory;
    salary      : Decimal(12,2) @assert.range: [0, 999999.99];
    isActive    : Boolean default true;
}

entity Departments : cuid {
    name : String(100) @mandatory;
    code : String(10)  @mandatory @assert.unique;
}
```

### CDS Service (srv/employee-service.cds)
```cds
using { sap.hr as hr } from '../db/schema';

service EmployeeService @(path: '/api/v1/employees') {
    
    @(requires: ['Manager', 'Admin'])
    entity Employees as projection on hr.Employees;
    
    @readonly
    entity Departments as projection on hr.Departments;
}
```

### Existing Handler Pattern
```javascript
const cds = require('@sap/cds');
const LOG = cds.log('hr');

class EmployeeService extends cds.ApplicationService {
    async init() {
        const { Departments } = this.entities;
        
        this.before('CREATE', Departments, this.validateDepartment);
        
        await super.init();
    }
    
    async validateDepartment(req) {
        const { name, code } = req.data;
        if (!name?.trim()) req.error(400, 'Department name is required', 'name');
        if (code && !/^[A-Z]{2,5}$/.test(code)) {
            req.error(400, 'Code must be 2-5 uppercase letters', 'code');
        }
    }
}

module.exports = EmployeeService;
```

### Team Standards
- Use CDS `@assert` annotations for declarative validation where possible
- Use `before` handler for business logic validation
- Error messages: user-friendly, field-specific
- Use `req.error()` (not throw) — allows multiple errors to accumulate
- Log validation failures at `warn` level
- Email domain must be `@company.com` for internal employees

---

## Task
Add comprehensive input validation for the Employees entity CREATE operation:
1. Leverage existing CDS annotations (they're already declared)
2. Add business logic validation in the handler:
   - Email must be `@company.com` domain
   - Hire date cannot be in the future
   - Salary must be appropriate for the position level
   - Department must exist and be active
3. Follow the existing handler pattern (see validateDepartment)

## Expected Output
- Updated handler with validation
- Any CDS model updates if annotations should be added
```

---

## The AI Response

### CDS Model Update (minor addition)

```cds
// Add to schema.cds - enhanced annotations
entity Employees : cuid, managed {
    firstName   : String(100) @mandatory;
    lastName    : String(100) @mandatory;
    email       : String(200) @mandatory @assert.format: '[^@]+@company\.com$';
    department  : Association to Departments @mandatory;
    position    : String(100);
    hireDate    : Date        @mandatory;
    salary      : Decimal(12,2) @assert.range: [0, 999999.99];
    isActive    : Boolean default true;
}
```

### Updated Handler

```javascript
const cds = require('@sap/cds');
const LOG = cds.log('hr');

class EmployeeService extends cds.ApplicationService {
    async init() {
        const { Employees, Departments } = this.entities;

        this.before('CREATE', Employees, this.validateEmployee);
        this.before('CREATE', Departments, this.validateDepartment);

        await super.init();
    }

    // ============================
    // Employee Validation
    // ============================
    async validateEmployee(req) {
        const { firstName, lastName, email, department_ID, hireDate, salary, position } = req.data;

        // --- Name validation ---
        if (!firstName?.trim()) {
            req.error(400, 'First name is required', 'firstName');
        }
        if (!lastName?.trim()) {
            req.error(400, 'Last name is required', 'lastName');
        }

        // --- Email validation (business rule: must be company domain) ---
        if (email) {
            if (!email.endsWith('@company.com')) {
                req.error(400,
                    'Email must be a @company.com address',
                    'email'
                );
            }

            // Check uniqueness
            const existing = await SELECT.one
                .from('sap.hr.Employees')
                .where({ email, isActive: true });

            if (existing) {
                req.error(409,
                    `An active employee with email ${email} already exists`,
                    'email'
                );
            }
        }

        // --- Hire date validation ---
        if (hireDate) {
            const hire = new Date(hireDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            if (hire > today) {
                req.error(400,
                    'Hire date cannot be in the future',
                    'hireDate'
                );
            }
        }

        // --- Department validation ---
        if (department_ID) {
            const dept = await SELECT.one
                .from('sap.hr.Departments')
                .where({ ID: department_ID });

            if (!dept) {
                req.error(400,
                    'Selected department does not exist',
                    'department_ID'
                );
            }
        }

        // --- Salary reasonableness check ---
        if (salary !== undefined && salary !== null) {
            if (salary < 0) {
                req.error(400, 'Salary cannot be negative', 'salary');
            }

            // Position-based salary bands (business rule)
            const salaryBands = {
                'Junior':   { min: 30000, max: 60000 },
                'Senior':   { min: 55000, max: 120000 },
                'Lead':     { min: 90000, max: 180000 },
                'Director': { min: 150000, max: 350000 },
            };

            if (position && salaryBands[position]) {
                const band = salaryBands[position];
                if (salary < band.min || salary > band.max) {
                    req.warn(
                        `Salary ${salary} is outside the typical range for ` +
                        `${position} (${band.min}-${band.max}). Proceeding anyway.`,
                        'salary'
                    );
                }
            }
        }

        // Log validation attempt
        if (req.errors?.length) {
            LOG.warn('Employee validation failed', {
                errors: req.errors.length,
                user: req.user.id
            });
        }
    }

    // ============================
    // Department Validation (existing)
    // ============================
    async validateDepartment(req) {
        const { name, code } = req.data;
        if (!name?.trim()) req.error(400, 'Department name is required', 'name');
        if (code && !/^[A-Z]{2,5}$/.test(code)) {
            req.error(400, 'Code must be 2-5 uppercase letters', 'code');
        }
    }
}

module.exports = EmployeeService;
```

---

## The Developer's Experience

```
Time: 0:00  → Assembled context (had template ready): 2 minutes
Time: 2:00  → Sent prompt with context
Time: 2:30  → Received response
Time: 3:00  → Reviewed: matches our patterns ✅
Time: 3:30  → Minor tweak: adjusted salary bands to actual values
Time: 4:00  → Pasted into codebase, tests pass

Total time: 4 minutes
Usable on first try: YES ✅
Rounds of correction: 0
Developer satisfaction: HIGH 😊
```

---

## Side-by-Side Comparison

| Metric | Without Context | With Context |
|--------|----------------|--------------|
| **Time to usable output** | 12 minutes | 4 minutes |
| **Correction rounds** | 5 | 0 |
| **Framework accuracy** | ❌ Wrong (Express) | ✅ Correct (CAP) |
| **Pattern compliance** | ❌ Custom patterns | ✅ Matches team patterns |
| **Auth handling** | ❌ Missing | ✅ XSUAA-aware |
| **Error format** | ❌ Plain JSON | ✅ CDS req.error() |
| **Business rules** | ❌ Generic | ✅ Company-specific |
| **Production-ready** | ❌ Toy example | ✅ Mergeable code |

---

## What Made the Difference

| Context Provided | Impact |
|-----------------|--------|
| CDS model with annotations | AI used correct entity names, types, and leveraged existing `@assert` |
| Existing handler pattern | Output follows class-based handler, `req.error()`, same code style |
| Team standards list | Used `req.error()` accumulation, `warn` level for non-blocking issues |
| Business rule (email domain) | Validated against `@company.com` specifically |
| SAP-specific stack | Used CAP patterns, not Express/generic Node.js |

---

> *The context took 2 minutes to assemble. It saved 8 minutes of back-and-forth and produced production-ready code on the first try.*
>
> *That's the power of Context Injection.*
