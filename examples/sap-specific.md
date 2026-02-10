# Example: SAP-Specific Workflows with Context Injection

## Scenario

A developer is building a CAP (Cloud Application Programming) application on SAP BTP and needs to implement a custom handler for a CDS service with proper authorization, input validation, and SAP HANA-specific optimizations.

---

## ❌ Without Context Injection

**Prompt:**
> How do I create a custom handler in CAP for a POST request?

**AI Response:**
> In CAP Node.js, you can register a custom handler like this:
> ```javascript
> module.exports = cds.service.impl(async function() {
>     this.on('CREATE', 'MyEntity', async (req) => {
>         // custom logic
>         return req.data;
>     });
> });
> ```
> Make sure to register the handler in your service implementation file.

*Bare-bones example. Ignores authorization, validation, SAP-specific patterns, HANA optimization, and project structure.*

---

## ✅ With Context Injection

**Prompt:**

```markdown
## Context

### Project
- **Name:** Procurement Approval Workflow
- **Stack:** SAP CAP (Node.js), SAP HANA Cloud, SAP BTP Cloud Foundry
- **CAP Version:** @sap/cds 7.5, @sap/cds-dk 7.5
- **Node Version:** 18.x (LTS)
- **Architecture:** Domain-driven, following SAP CAP best practices

### CDS Model (db/schema.cds)
```cds
namespace sap.procurement;

using { cuid, managed, sap.common.CodeList } from '@sap/cds/common';

entity PurchaseRequests : cuid, managed {
    title        : String(200)  @mandatory;
    description  : String(5000);
    amount       : Decimal(15,2) @mandatory;
    currency     : Currency;
    status       : Association to RequestStatuses;
    priority     : String enum { LOW; MEDIUM; HIGH; CRITICAL };
    department   : Association to Departments;
    items        : Composition of many RequestItems on items.request = $self;
    approver     : Association to Approvers;
    approvedAt   : Timestamp;
    rejectedAt   : Timestamp;
    rejectionNote: String(1000);
}

entity RequestItems : cuid {
    request     : Association to PurchaseRequests;
    product     : String(200) @mandatory;
    quantity    : Integer     @mandatory;
    unitPrice   : Decimal(15,2);
    totalPrice  : Decimal(15,2);
}

entity RequestStatuses : CodeList {
    key code : String(20); // DRAFT, SUBMITTED, APPROVED, REJECTED
}

entity Departments : CodeList {
    key code : String(20);
    budget   : Decimal(15,2);
}

entity Approvers : cuid, managed {
    name        : String(100);
    email       : String(200);
    maxAmount   : Decimal(15,2); // max approval authority
    department  : Association to Departments;
}
```

### CDS Service (srv/procurement-service.cds)
```cds
using { sap.procurement as proc } from '../db/schema';

service ProcurementService @(path: '/api/procurement') {
    
    @(requires: ['Employee', 'Manager', 'Admin'])
    entity PurchaseRequests as projection on proc.PurchaseRequests {
        *, items: redirected to RequestItems
    } actions {
        @(requires: 'Manager')
        action approve();
        
        @(requires: 'Manager')  
        action reject(note: String(1000) @mandatory);
        
        @(requires: ['Employee', 'Manager'])
        action submit();
    };
    
    @readonly
    entity RequestItems as projection on proc.RequestItems;
    
    @readonly @(requires: 'Admin')
    entity Departments as projection on proc.Departments;
}
```

### Authorization Setup
- **IDP:** SAP Identity Authentication Service (IAS)
- **XSUAA:** Configured with role collections: `Employee`, `Manager`, `Admin`
- **Business rules:**
  - Employees can create and submit requests for their own department
  - Managers can approve/reject requests ≤ their `maxAmount`
  - Requests > manager's limit must be escalated (not auto-approved)
  - Admins can view everything but not approve

### SAP-Specific Requirements
1. Use `@sap/cds` built-in validation, not custom middleware
2. Follow **SAP Clean Core** principles
3. Use `cds.log()` for structured logging (not console.log)
4. Handle deep inserts (request + items in single POST)
5. Calculate `totalPrice` on items automatically (server-side)
6. Set initial status to `DRAFT` on create
7. Emit SAP Event Mesh events on status changes for downstream integration

### Existing Handler Pattern (from another service in the project)
```javascript
const cds = require('@sap/cds');
const LOG = cds.log('inventory');

class InventoryService extends cds.ApplicationService {
    async init() {
        const { Products } = this.entities;
        
        this.before('CREATE', Products, this.validateProduct);
        this.after('CREATE', Products, this.notifyWarehouse);
        
        await super.init();
    }
    
    async validateProduct(req) {
        const { name, sku } = req.data;
        if (!name?.trim()) req.error(400, 'Product name is required', 'name');
        if (!sku?.match(/^[A-Z]{3}-\d{6}$/)) req.error(400, 'Invalid SKU format', 'sku');
    }
    
    async notifyWarehouse(data, req) {
        const messaging = await cds.connect.to('messaging');
        await messaging.emit('sap/inventory/ProductCreated', { productId: data.ID });
    }
}

module.exports = ProcurementService;
```

### package.json (relevant parts)
```json
{
  "dependencies": {
    "@sap/cds": "^7.5",
    "@sap/xssec": "^3.6",
    "@sap-cloud-sdk/http-client": "^3.10"
  },
  "cds": {
    "requires": {
      "auth": {
        "kind": "xsuaa"
      },
      "db": {
        "kind": "hana-cloud"
      },
      "messaging": {
        "kind": "enterprise-messaging"
      }
    }
  }
}
```

---

## Task
Implement the complete service handler (`srv/procurement-service.js`) for the ProcurementService with:

1. **CREATE handler:** Deep insert support, auto-calculate item totals, set status to DRAFT, validate amount > 0
2. **submit action:** Validate all required fields are filled, change status to SUBMITTED, emit event
3. **approve action:** Verify manager's maxAmount authority, change status to APPROVED, set approvedAt, emit event
4. **reject action:** Validate rejection note provided, change status to REJECTED, set rejectedAt, emit event
5. **Authorization:** Employees can only see/edit their own department's requests
6. Follow the existing handler pattern from InventoryService

## Output
Complete handler file with inline comments explaining SAP-specific patterns
```

**AI Response:**

```javascript
const cds = require('@sap/cds');
const LOG = cds.log('procurement');

class ProcurementService extends cds.ApplicationService {
    async init() {
        const { PurchaseRequests, RequestItems } = this.entities;

        // --- Validation Hooks ---
        this.before('CREATE', PurchaseRequests, this.onBeforeCreate);
        this.before('UPDATE', PurchaseRequests, this.onBeforeUpdate);

        // --- Deep Insert: Calculate item totals ---
        this.before('NEW', RequestItems, this.calculateItemTotal);
        this.before('SAVE', RequestItems, this.calculateItemTotal);

        // --- Authorization: Department-scoped access ---
        this.before('READ', PurchaseRequests, this.restrictByDepartment);

        // --- Bound Actions ---
        this.on('submit', PurchaseRequests, this.onSubmit);
        this.on('approve', PurchaseRequests, this.onApprove);
        this.on('reject', PurchaseRequests, this.onReject);

        await super.init();
    }

    // ============================
    // CREATE Handler
    // ============================
    async onBeforeCreate(req) {
        const { amount, items } = req.data;

        // Validate amount
        if (amount !== undefined && amount <= 0) {
            req.error(400, 'Amount must be greater than zero', 'amount');
        }

        // Set default status to DRAFT
        // Using code-list association pattern (SAP CAP convention)
        req.data.status_code = 'DRAFT';

        // Calculate item totals for deep insert
        if (items?.length) {
            let calculatedTotal = 0;
            for (const item of items) {
                if (item.quantity && item.unitPrice) {
                    item.totalPrice = item.quantity * item.unitPrice;
                    calculatedTotal += item.totalPrice;
                }
            }
            // Auto-set amount from items if not explicitly provided
            if (!amount && calculatedTotal > 0) {
                req.data.amount = calculatedTotal;
            }
        }

        LOG.info('Purchase request created', {
            title: req.data.title,
            amount: req.data.amount,
            user: req.user.id
        });
    }

    // ============================
    // UPDATE Handler
    // ============================
    async onBeforeUpdate(req) {
        // Only DRAFT requests can be edited
        const current = await SELECT.one.from('sap.procurement.PurchaseRequests')
            .where({ ID: req.data.ID })
            .columns('status_code');

        if (current?.status_code !== 'DRAFT') {
            req.error(409, 'Only DRAFT requests can be modified');
        }
    }

    // ============================
    // Item Total Calculation
    // ============================
    calculateItemTotal(req) {
        const { quantity, unitPrice } = req.data;
        if (quantity && unitPrice) {
            req.data.totalPrice = quantity * unitPrice;
        }
    }

    // ============================
    // Authorization: Department Scope
    // ============================
    async restrictByDepartment(req) {
        // Admins can see everything (per business rules)
        if (req.user.is('Admin')) return;

        // Employees and Managers see only their department
        // User's department is stored as XSUAA attribute
        const userDept = req.user.attr?.department;
        if (userDept) {
            // CDS query manipulation — SAP CAP's way to add WHERE clauses
            req.query.where({ department_code: userDept });
        }
    }

    // ============================
    // Action: Submit
    // ============================
    async onSubmit(req) {
        const { ID } = req.params[0];

        const request = await SELECT.one
            .from('sap.procurement.PurchaseRequests')
            .where({ ID })
            .columns('*');

        // Validate: must be in DRAFT status
        if (request.status_code !== 'DRAFT') {
            return req.error(409, `Cannot submit: request is in ${request.status_code} status`);
        }

        // Validate: required fields for submission
        if (!request.title?.trim()) {
            return req.error(400, 'Title is required for submission', 'title');
        }
        if (!request.amount || request.amount <= 0) {
            return req.error(400, 'Valid amount is required for submission', 'amount');
        }
        if (!request.department_code) {
            return req.error(400, 'Department is required for submission', 'department_code');
        }

        // Validate: must have at least one item
        const items = await SELECT.from('sap.procurement.RequestItems')
            .where({ request_ID: ID });

        if (!items?.length) {
            return req.error(400, 'At least one item is required for submission');
        }

        // Update status
        await UPDATE('sap.procurement.PurchaseRequests')
            .set({ status_code: 'SUBMITTED' })
            .where({ ID });

        // Emit event for downstream consumers (SAP Event Mesh)
        const messaging = await cds.connect.to('messaging');
        await messaging.emit('sap/procurement/RequestSubmitted', {
            requestId: ID,
            amount: request.amount,
            department: request.department_code,
            submittedBy: req.user.id
        });

        LOG.info('Purchase request submitted', { ID, user: req.user.id });

        // Return updated entity (CAP convention for bound actions)
        return SELECT.one.from('sap.procurement.PurchaseRequests').where({ ID });
    }

    // ============================
    // Action: Approve
    // ============================
    async onApprove(req) {
        const { ID } = req.params[0];

        const request = await SELECT.one
            .from('sap.procurement.PurchaseRequests')
            .where({ ID })
            .columns('*');

        // Must be SUBMITTED
        if (request.status_code !== 'SUBMITTED') {
            return req.error(409, `Cannot approve: request is in ${request.status_code} status`);
        }

        // Check manager's approval authority
        const approver = await SELECT.one
            .from('sap.procurement.Approvers')
            .where({ email: req.user.id });

        if (!approver) {
            return req.error(403, 'You are not registered as an approver');
        }

        if (request.amount > approver.maxAmount) {
            return req.error(403,
                `Amount ${request.amount} exceeds your approval limit of ${approver.maxAmount}. ` +
                `This request requires escalation.`
            );
        }

        // Approve
        const now = new Date().toISOString();
        await UPDATE('sap.procurement.PurchaseRequests')
            .set({
                status_code: 'APPROVED',
                approver_ID: approver.ID,
                approvedAt: now
            })
            .where({ ID });

        // Emit event
        const messaging = await cds.connect.to('messaging');
        await messaging.emit('sap/procurement/RequestApproved', {
            requestId: ID,
            amount: request.amount,
            approvedBy: req.user.id,
            approvedAt: now
        });

        LOG.info('Purchase request approved', {
            ID,
            amount: request.amount,
            approver: req.user.id
        });

        return SELECT.one.from('sap.procurement.PurchaseRequests').where({ ID });
    }

    // ============================
    // Action: Reject
    // ============================
    async onReject(req) {
        const { ID } = req.params[0];
        const { note } = req.data;

        // Validate rejection note (also enforced by @mandatory in CDS, belt & suspenders)
        if (!note?.trim()) {
            return req.error(400, 'Rejection note is required', 'note');
        }

        const request = await SELECT.one
            .from('sap.procurement.PurchaseRequests')
            .where({ ID })
            .columns('status_code', 'amount', 'title');

        if (request.status_code !== 'SUBMITTED') {
            return req.error(409, `Cannot reject: request is in ${request.status_code} status`);
        }

        const now = new Date().toISOString();
        await UPDATE('sap.procurement.PurchaseRequests')
            .set({
                status_code: 'REJECTED',
                rejectedAt: now,
                rejectionNote: note
            })
            .where({ ID });

        // Emit event
        const messaging = await cds.connect.to('messaging');
        await messaging.emit('sap/procurement/RequestRejected', {
            requestId: ID,
            rejectedBy: req.user.id,
            rejectedAt: now,
            note
        });

        LOG.info('Purchase request rejected', {
            ID,
            rejector: req.user.id,
            note: note.substring(0, 100)
        });

        return SELECT.one.from('sap.procurement.PurchaseRequests').where({ ID });
    }
}

module.exports = ProcurementService;
```

*Complete handler with SAP-specific patterns, authorization, event emission, and structured logging — matching the project's existing conventions exactly.*

---

## Key Takeaways

| Context Element | What It Enabled |
|----------------|-----------------|
| Full CDS model | AI used correct entity names, associations, and types |
| CDS service definition | Handler matches declared actions and auth annotations |
| Existing handler pattern | Output follows team's class-based handler style |
| XSUAA + role setup | Authorization logic uses correct role checks |
| Business rules | Manager approval limit enforcement |
| SAP Event Mesh config | Event emission follows messaging setup from package.json |
| Clean Core requirement | No custom middleware, uses CAP built-in patterns |

**Without context:** A 5-line generic handler.
**With context:** 200+ lines of production-ready, SAP-compliant code that follows every team convention.
