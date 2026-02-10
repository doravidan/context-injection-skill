# Example: Architecture Decision with Context Injection

## Scenario

A tech lead needs to decide between two approaches for implementing event-driven communication between microservices and wants to draft an ADR (Architecture Decision Record).

---

## ❌ Without Context Injection

**Prompt:**
> Should I use Kafka or RabbitMQ for microservice communication?

**AI Response:**
> Here's a comparison:
> | Feature | Kafka | RabbitMQ |
> |---------|-------|----------|
> | Throughput | High | Medium |
> | Ordering | Per partition | Per queue |
> ...
> 
> Choose Kafka for high throughput and log-based streaming. Choose RabbitMQ for simpler routing and traditional messaging.

*A generic comparison table from any blog post. Doesn't help make the actual decision.*

---

## ✅ With Context Injection

**Prompt:**

```markdown
## Context

### Project
- **Name:** SAP Order Management Platform
- **Domain:** B2B e-commerce for industrial supplies
- **Stack:** Java 17 (Spring Boot), SAP BTP Cloud Foundry, SAP HANA Cloud
- **Services:** 6 microservices (Order, Inventory, Pricing, Shipping, Notification, Analytics)
- **Current state:** Synchronous REST calls between all services
- **Team size:** 8 developers, 2 with Kafka experience, 0 with RabbitMQ

### The Problem We're Solving
- **Cascading failures:** When Inventory service goes down, Order service hangs (30s timeout), causing user-facing errors
- **Peak load:** During quarterly procurement cycles, order volume spikes 10x (from 50 to 500 orders/minute)
- **Data consistency:** Order → Inventory → Pricing must stay in sync; eventual consistency is acceptable (< 5s lag)
- **Audit trail:** Compliance requires full audit log of all order state changes (7-year retention)

### Communication Patterns Needed
1. **Order Created** → Inventory (reserve stock), Pricing (calculate), Notification (confirm)
2. **Inventory Updated** → Order (stock status), Analytics (reporting)
3. **Order Completed** → Shipping (dispatch), Analytics, Notification
4. **Price Changed** → Order (recalculate pending orders) — needs to be processed IN ORDER per customer

### Constraints
- **SAP BTP:** Must run on SAP BTP or be available as managed service from BTP Service Marketplace
- **Budget:** €500/month max for messaging infrastructure
- **Ops capacity:** No dedicated DevOps team; must be low operational overhead
- **Compliance:** GDPR (EU data residency), audit logging required
- **Timeline:** 3 months to production

### Options Under Consideration

**Option A: SAP Event Mesh (BTP-native)**
- Managed service on SAP BTP
- Supports AMQP, MQTT, REST
- Built-in SAP integration (S/4HANA events, CAP framework support)
- Pricing: ~€300/month for our projected volume

**Option B: Apache Kafka (Confluent Cloud)**
- Industry standard for event streaming
- Available via BTP Service Marketplace (Confluent partnership)
- Log-based, excellent for audit trail and replay
- Pricing: ~€450/month (Basic cluster + storage)

**Option C: SAP Integration Suite (Advanced Event Mesh - Solace)**
- Enterprise-grade, part of SAP Integration Suite
- Supports hybrid scenarios (on-prem S/4 to cloud)
- Pricing: ~€600/month (over budget but negotiable)

### Existing Decisions
- ADR-003: "We use SAP BTP managed services over self-hosted when available"
- ADR-005: "Data must reside in EU (Frankfurt region)"
- ADR-008: "Prefer SAP-native solutions for core integration patterns"

### Future Considerations
- Phase 2 will integrate with on-premise SAP S/4HANA (hybrid events)
- Analytics team wants to replay historical events for ML model training

---

## Task
1. Evaluate the three options against our specific requirements
2. Recommend one with clear justification
3. Draft an ADR in our standard format:
   - Title, Status, Context, Decision, Consequences

## Output Format
Evaluation matrix + complete ADR document
```

**AI Response:**

### Evaluation Matrix

| Requirement | SAP Event Mesh | Kafka (Confluent) | SAP AEM (Solace) |
|------------|---------------|-------------------|------------------|
| BTP-native (ADR-003) | ✅ Native | ⚠️ Marketplace | ✅ Native |
| EU data residency | ✅ Frankfurt | ✅ Frankfurt | ✅ Frankfurt |
| Budget (€500/mo) | ✅ €300 | ✅ €450 | ❌ €600 |
| Audit trail (7yr) | ⚠️ Limited retention | ✅ Log-based, replay | ✅ Configurable |
| Ordered processing | ⚠️ Per-queue | ✅ Per-partition key | ✅ Per-topic |
| S/4HANA integration | ✅ Native events | ⚠️ Requires adapter | ✅ Native |
| Team experience | 🟡 New to team | ✅ 2 devs know Kafka | 🟡 New to team |
| Operational overhead | ✅ Fully managed | ✅ Managed (Confluent) | ✅ Fully managed |
| Event replay (Phase 2) | ❌ Not supported | ✅ Core capability | ⚠️ Limited |
| SAP-native (ADR-008) | ✅ | ⚠️ | ✅ |

### Recommendation: **SAP Event Mesh** for Phase 1, with **migration path to Kafka** for Phase 2

### ADR-012: Event-Driven Communication Between Microservices

**Status:** Proposed

**Context:**

Our Order Management Platform currently uses synchronous REST communication between 6 microservices. This causes cascading failures during Inventory service outages and cannot handle 10x peak load spikes during quarterly procurement cycles. We need asynchronous, event-driven communication with ordered processing guarantees and a 7-year audit trail for compliance.

We evaluated three options: SAP Event Mesh, Apache Kafka (Confluent Cloud), and SAP Advanced Event Mesh (Solace).

**Decision:**

We will adopt **SAP Event Mesh** as our messaging infrastructure for Phase 1, with the following provisions:

1. SAP Event Mesh meets our core requirements: BTP-native (ADR-003), SAP-native (ADR-008), EU data residency (ADR-005), and within budget at €300/month
2. For the audit trail requirement, we will implement an **Event Store pattern**: a dedicated consumer that persists all events to a SAP HANA Cloud table with 7-year retention
3. For ordered processing (price changes per customer), we will use queue subscriptions with customer-based routing

**For Phase 2** (S/4HANA integration and event replay), we will re-evaluate and potentially migrate to Kafka (Confluent Cloud) if SAP Event Mesh cannot support replay requirements. We will design our event schemas and producer interfaces to be transport-agnostic to minimize migration cost.

**Consequences:**

**Positive:**
- Fully managed, zero operational overhead
- Native CAP framework integration reduces development time
- Aligned with existing ADRs (003, 005, 008)
- Within budget with room for growth
- Future S/4HANA integration is straightforward

**Negative:**
- Limited event replay capability (requires custom Event Store)
- Team needs training on SAP Event Mesh (1-2 weeks ramp-up)
- If Phase 2 requires Kafka, migration effort estimated at 2-3 weeks
- Less community ecosystem compared to Kafka

**Risks:**
- SAP Event Mesh may not scale to Phase 2 requirements → mitigated by transport-agnostic design
- Event Store adds custom code for audit trail → mitigated by using standard SAP HANA persistence

---

## Key Takeaways

| Context Element | What It Enabled |
|----------------|-----------------|
| Specific communication patterns | Evaluation addressed actual use cases, not hypotheticals |
| Existing ADRs | Recommendation aligned with established decisions |
| Budget constraint | Eliminated Option C immediately |
| Team experience | Factored Kafka experience into evaluation |
| Phase 2 requirements | Designed for migration path, not just immediate needs |
| Compliance requirements | Proposed Event Store pattern for audit trail |

**Without context:** Generic Kafka vs. RabbitMQ comparison.
**With context:** Actionable decision with complete ADR, evaluation matrix, and migration strategy.
