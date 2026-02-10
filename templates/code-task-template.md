# Code Task Template

> Use this template for implementation, debugging, refactoring, and code review tasks.

---

## Template

```markdown
## Context

### Project
- **Name:** [Project name]
- **Stack:** [Language version, framework, key libs]
- **Architecture:** [Pattern: MVC, hexagonal, microservices, etc.]
- **Module:** [Specific module/package this task is in]

### Relevant Code

**[filename1]:**
```[language]
[paste relevant code — interfaces, models, related classes]
```

**[filename2]:**
```[language]
[paste additional relevant code if needed]
```

### Standards & Conventions
- [Convention 1: e.g., "Constructor injection only"]
- [Convention 2: e.g., "All public methods must have Javadoc"]
- [Convention 3: e.g., "Use Optional instead of null returns"]

### Error/Logs (if debugging)
```
[paste stack trace, error message, or relevant log output]
```

### What's Been Tried (if debugging)
- [Previous attempt 1 and why it failed]
- [Previous attempt 2 and why it failed]

---

## Task
[Specific, actionable request]

## Acceptance Criteria
1. [Criterion 1]
2. [Criterion 2]
3. [Criterion 3]

## Expected Output
- [ ] Source code changes
- [ ] Unit tests
- [ ] Brief explanation of approach
```

---

## When to Use

- Implementing new features (single service or module)
- Fixing bugs with known error output
- Refactoring existing code
- Writing tests for existing code
- Code review assistance

---

## Example: Filled In

```markdown
## Context

### Project
- **Name:** SAP Commerce Storefront API
- **Stack:** Java 17, Spring Boot 3.2, PostgreSQL 15
- **Architecture:** Hexagonal (ports & adapters)
- **Module:** `order-service` (handles order lifecycle)

### Relevant Code

**OrderPort.java (port interface):**
```java
public interface OrderPort {
    Order createOrder(CreateOrderCommand command);
    Optional<Order> findById(UUID orderId);
    List<Order> findByCustomer(UUID customerId);
    // TODO: Add cancellation support
}
```

**OrderAdapter.java (existing implementation):**
```java
@Component
@RequiredArgsConstructor
public class OrderAdapter implements OrderPort {
    private final OrderRepository repository;
    private final OrderMapper mapper;
    
    @Override
    @Transactional
    public Order createOrder(CreateOrderCommand command) {
        OrderEntity entity = mapper.toEntity(command);
        entity.setStatus(OrderStatus.CREATED);
        OrderEntity saved = repository.save(entity);
        return mapper.toDomain(saved);
    }
    
    @Override
    @Transactional(readOnly = true)
    public Optional<Order> findById(UUID orderId) {
        return repository.findById(orderId).map(mapper::toDomain);
    }
    
    // ... findByCustomer implementation
}
```

**Order.java (domain model):**
```java
public record Order(
    UUID id,
    UUID customerId,
    List<OrderLine> lines,
    OrderStatus status,
    Instant createdAt,
    Instant cancelledAt,
    String cancellationReason
) {}
```

### Standards & Conventions
- Hexagonal architecture: all logic in domain, adapters are thin
- Use `record` for domain models, `@Entity` classes for persistence
- All state changes must emit domain events
- Constructor injection via Lombok `@RequiredArgsConstructor`
- Tests: JUnit 5 + Mockito, follow Given/When/Then pattern

### Error/Logs
N/A — new feature implementation

---

## Task
Add order cancellation support:
1. Add `cancelOrder(UUID orderId, String reason)` to the port and adapter
2. Only orders in CREATED or CONFIRMED status can be cancelled
3. Emit an `OrderCancelledEvent` on successful cancellation

## Acceptance Criteria
1. Port interface updated with cancel method
2. Adapter implements cancellation with status validation
3. Domain event emitted after cancellation
4. Unit tests for success case and invalid-status rejection
5. Follows existing patterns (see OrderAdapter)

## Expected Output
- [ ] Updated port interface
- [ ] Updated adapter implementation
- [ ] Domain event class
- [ ] Unit test class
- [ ] Brief explanation
```

---

## Tips

1. **Include the interfaces** — The AI needs to see the contracts it must implement
2. **Show an existing example** — Include a similar, already-implemented method for the AI to follow
3. **State conventions explicitly** — "Constructor injection" is better than hoping the AI notices your pattern
4. **List acceptance criteria** — These become the AI's checklist for completeness
5. **Include what was tried** — For debugging, this prevents the AI from suggesting failed approaches
