# Example: Code Review with Context Injection

## Scenario

A team lead wants AI assistance reviewing a pull request that adds a new REST endpoint for user profile updates.

---

## ❌ Without Context Injection

**Prompt:**
> Review this code:
> ```java
> @PutMapping("/users/{id}")
> public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody UserDTO dto) {
>     User user = userRepo.findById(id).orElseThrow();
>     user.setName(dto.getName());
>     user.setEmail(dto.getEmail());
>     userRepo.save(user);
>     return ResponseEntity.ok(user);
> }
> ```

**AI Response:**
> The code looks functional. Some suggestions:
> - Add validation for the DTO
> - Handle the exception from `orElseThrow()`
> - Consider returning a DTO instead of the entity
> 
> Overall, it's a standard Spring Boot update endpoint.

*Surface-level review. Misses project-specific issues entirely.*

---

## ✅ With Context Injection

**Prompt:**

```markdown
## Context

### Project
- **Name:** SAP BTP User Management Service
- **Stack:** Java 17, Spring Boot 3.2, SAP HANA Cloud
- **Architecture:** Hexagonal (ports & adapters), CQRS for user operations
- **Auth:** SAP XSUAA with JWT, role-based access control

### Review Checklist (team standard)
Our code reviews MUST check for:
1. **Security:** Input validation, authorization checks, data exposure
2. **Architecture:** Adherence to hexagonal architecture (no repo in controller)
3. **Error handling:** Custom exceptions, proper HTTP status codes
4. **Observability:** Logging at appropriate levels
5. **Testing:** Unit + integration tests included in PR
6. **API conventions:** DTOs for input/output, HATEOAS links, versioned paths

### Existing Patterns in Codebase

**Controller pattern (what we follow):**
```java
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {
    
    private final UserCommandService userCommandService; // port, not repo
    
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN') or #id == authentication.principal.userId")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable UUID id,
            @Valid @RequestBody UpdateUserCommand command) {
        
        UserResponse response = userCommandService.updateUser(id, command);
        return ResponseEntity.ok(response);
    }
}
```

**Standard error handling:**
```java
@ControllerAdvice
public class GlobalExceptionHandler {
    // ResourceNotFoundException → 404
    // ValidationException → 400
    // UnauthorizedException → 403
}
```

### PR Under Review (SHOP-4590)

**Author's code:**
```java
@PutMapping("/users/{id}")
public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody UserDTO dto) {
    User user = userRepo.findById(id).orElseThrow();
    user.setName(dto.getName());
    user.setEmail(dto.getEmail());
    userRepo.save(user);
    return ResponseEntity.ok(user);
}
```

**PR description:** "Added user update endpoint"
**No tests included in PR.**

---

## Task
Review this PR against our team's standards and checklist. For each issue found:
1. State the category (Security, Architecture, etc.)
2. Explain what's wrong
3. Show the corrected code

Rate severity: 🔴 Blocker, 🟡 Major, 🟢 Minor
```

**AI Response:**

### Review Findings

#### 🔴 Blocker: Missing Authorization Check
**Category:** Security
```java
// ❌ Current: No auth check — any authenticated user can update any profile
@PutMapping("/users/{id}")

// ✅ Required: Role-based + ownership check
@PutMapping("/{id}")
@PreAuthorize("hasRole('ADMIN') or #id == authentication.principal.userId")
```

#### 🔴 Blocker: Repository Injected Directly in Controller
**Category:** Architecture
```java
// ❌ Current: Violates hexagonal architecture
private final UserRepo userRepo;

// ✅ Required: Use the command service (port)
private final UserCommandService userCommandService;
```

#### 🔴 Blocker: Entity Exposed in API Response
**Category:** Security / API Conventions
```java
// ❌ Current: Returns JPA entity (leaks internal fields, lazy-loading issues)
return ResponseEntity.ok(user);

// ✅ Required: Return response DTO
return ResponseEntity.ok(UserResponse.from(user));
```

#### 🟡 Major: No Input Validation
**Category:** Security
```java
// ❌ Current: Raw DTO, no validation
@RequestBody UserDTO dto

// ✅ Required: Validated command object
@Valid @RequestBody UpdateUserCommand command
```

#### 🟡 Major: Missing API Versioning
**Category:** API Conventions
```java
// ❌ Current: Unversioned path
@PutMapping("/users/{id}")

// ✅ Required: Follows team convention
@RequestMapping("/api/v1/users")  // at class level
@PutMapping("/{id}")              // at method level
```

#### 🟡 Major: No Tests
**Category:** Testing

PR must include unit tests for the controller and integration tests for the endpoint.

#### 🟢 Minor: ID Type Mismatch
```java
// ❌ Current: Long id
@PathVariable Long id

// ✅ Team standard: UUID
@PathVariable UUID id
```

**Verdict:** ❌ **Request Changes** — 3 blockers must be resolved before merge.

---

## Key Takeaways

| Context Element | What It Enabled |
|----------------|-----------------|
| Review checklist | Structured, consistent review categories |
| Existing code patterns | AI identifies deviations from team standards |
| Architecture specification | Caught hexagonal architecture violation |
| Auth setup (XSUAA) | Identified missing `@PreAuthorize` |
| API conventions | Flagged versioning and DTO issues |

**Without context:** 3 generic suggestions. **With context:** 7 specific findings with corrected code, categorized by severity.
