# Enterprise Context Template

> Use this template for complex, cross-cutting tasks in enterprise environments — especially SAP projects, compliance-sensitive work, and architecture-level decisions.

---

## Template

```markdown
## Context

### Organization & Project
- **Company/Team:** [Team name, business unit]
- **Project:** [Project name and brief description]
- **Domain:** [Business domain: finance, procurement, HR, logistics, etc.]
- **Stack:** [Full technology stack with versions]
- **Environment:** [SAP BTP, S/4HANA, Cloud Foundry, Kubernetes, etc.]

### Architecture Overview
[Brief description of system architecture — microservices, modules, integration points]

```
[ASCII diagram or list of components and their relationships]
```

### Relevant Code / Configuration
**[file1]:**
```[language]
[relevant code]
```

**[file2]:**
```[language]
[relevant configuration]
```

### Standards & Governance
- **Architecture Decisions:** [Relevant ADRs: "ADR-003: Use SAP BTP managed services"]
- **Coding Standards:** [Key conventions]
- **Security & Compliance:** [GDPR, SOX, data classification, authorization model]
- **API Standards:** [Versioning, naming, pagination, error format]

### SAP-Specific Context (if applicable)
- **SAP Services Used:** [XSUAA, Event Mesh, HANA Cloud, Destination Service, etc.]
- **Integration Points:** [S/4HANA APIs, SuccessFactors, Ariba, etc.]
- **Authorization Model:** [Role collections, scopes, business rules]
- **Extension Pattern:** [Side-by-side, in-app, Clean Core compliance]

### Business Context
- **Why this task exists:** [Business driver, incident, strategic initiative]
- **Stakeholders:** [Who cares about this: product owner, compliance, security]
- **Timeline/Priority:** [Urgency, deadlines, SLA]
- **Dependencies:** [Other teams, services, or deliverables this depends on]

### Constraints
- [Technical constraint 1]
- [Organizational constraint 2]
- [Compliance constraint 3]
- [Budget/resource constraint 4]

### What Has Been Decided / Tried
- [Previous approach and outcome]
- [Relevant meeting decisions or Slack threads]
- [Existing ADR or design document excerpts]

---

## Task
[Clear, specific description of what needs to be done]

## Acceptance Criteria
1. [Business criterion]
2. [Technical criterion]
3. [Compliance criterion]
4. [Performance criterion]

## Expected Output
- [ ] [Deliverable 1: code, document, diagram, ADR, etc.]
- [ ] [Deliverable 2]
- [ ] [Deliverable 3]

## Out of Scope
- [What this task explicitly does NOT include]
- [Adjacent concerns to address later]
```

---

## When to Use

- Architecture decisions and ADR drafting
- Cross-service feature implementation
- Compliance-sensitive changes (auth, data handling, audit)
- Production incident investigation
- SAP-specific development (CAP, RAP, BTP services)
- Migration planning (monolith → microservices, on-prem → cloud)
- Security reviews and threat modeling

---

## Example: Filled In

```markdown
## Context

### Organization & Project
- **Company/Team:** SAP Labs Israel — Platform Engineering
- **Project:** Global Procurement Platform (GPP)
- **Domain:** Procurement / Supplier Management
- **Stack:** SAP CAP (Node.js 18), SAP HANA Cloud, SAP BTP CF (EU10)
- **Environment:** SAP BTP with SAP Event Mesh, SAP Build Work Zone

### Architecture Overview
Multi-tenant SaaS application with 3 microservices:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Supplier    │────▶│  Procurement │────▶│  Approval   │
│  Service     │     │  Service     │     │  Service    │
└──────┬──────┘     └──────┬───────┘     └──────┬──────┘
       │                   │                     │
       └───────────┬───────┘─────────────────────┘
                   ▼
          ┌────────────────┐
          │  SAP HANA Cloud│
          │  (shared HDI)  │
          └────────────────┘
```

### Relevant Code

**srv/procurement-service.cds:**
```cds
service ProcurementService @(path:'/api/v1/procurement') {
    entity PurchaseOrders as projection on db.PurchaseOrders;
    entity Suppliers as projection on db.Suppliers;
}
```

**mta.yaml (relevant section):**
```yaml
modules:
  - name: gpp-srv
    type: nodejs
    path: gen/srv
    requires:
      - name: gpp-auth
      - name: gpp-db
      - name: gpp-messaging
resources:
  - name: gpp-auth
    type: org.cloudfoundry.managed-service
    parameters:
      service: xsuaa
      service-plan: application
```

### Standards & Governance
- **ADR-003:** Use SAP BTP managed services over self-hosted
- **ADR-008:** Follow SAP Clean Core — no modifications to standard
- **Coding:** ESLint with SAP CAP recommended rules
- **Security:** GDPR Article 17 (right to erasure) must be supported
- **API:** OData v4 via CAP, versioned paths (/api/v1/...)

### SAP-Specific Context
- **Auth:** XSUAA with role collections per tenant
- **Multi-tenancy:** @sap/cds-mtxs for tenant provisioning
- **Events:** SAP Event Mesh for cross-service communication
- **Integration:** SAP S/4HANA Cloud APIs for PO sync (planned Phase 2)

### Business Context
- **Why:** Current supplier onboarding takes 3 weeks manual process
- **Goal:** Reduce to 3 days with automated approval workflow
- **Stakeholders:** VP Procurement (sponsor), Compliance (GDPR), InfoSec
- **Timeline:** MVP in 6 weeks, GA in 12 weeks

### Constraints
- Multi-tenant: all data must be tenant-isolated
- EU data residency (Frankfurt region only)
- Must support offline-capable mobile approval (SAP Mobile Start)
- Max 2 new BTP service instances (budget)

### What Has Been Decided
- Event-driven between services (not REST) — decided in arch review 2026-01-15
- Supplier data is master data owned by Supplier Service
- Approval workflow uses 3-level approval based on PO amount thresholds

---

## Task
Design and implement the event-driven supplier onboarding flow:
1. Supplier Service emits `SupplierCreated` event
2. Procurement Service subscribes and creates supplier record
3. Approval Service triggers 3-level approval workflow
4. On final approval, emit `SupplierApproved` event back

## Acceptance Criteria
1. Events flow correctly between all 3 services
2. Tenant isolation maintained in event payloads
3. Failed event processing retries 3x with exponential backoff
4. Full audit log of all state changes (GDPR)
5. Works with SAP Event Mesh topic patterns

## Expected Output
- [ ] Event schema definitions (CloudEvents format)
- [ ] CAP event handlers for all 3 services
- [ ] mta.yaml updates for Event Mesh bindings
- [ ] Error handling and retry logic
- [ ] Sequence diagram of the flow

## Out of Scope
- S/4HANA integration (Phase 2)
- Mobile UI (separate workstream)
- Supplier self-registration portal
```

---

## Tips

1. **Include the architecture diagram** — Even ASCII art helps the AI understand component relationships
2. **Reference ADRs by number** — This signals that decisions have been made and shouldn't be revisited
3. **State compliance requirements explicitly** — GDPR, SOX, data residency affect every design choice
4. **Define out of scope** — Prevents the AI from over-engineering or addressing adjacent concerns
5. **Include business context** — The "why" helps the AI make trade-off decisions correctly
6. **Mention SAP services by name** — SAP-specific context helps the AI use the right APIs and patterns
7. **Time-box the output** — "MVP in 6 weeks" influences the solution's complexity
