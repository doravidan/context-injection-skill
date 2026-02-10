# Test Results: Code Fix (NullPointer Bug)

**Test Date:** 2026-02-10  
**Model:** Claude Opus 4.6  
**Test Case:** `test_code_fix.json`

---

## ❌ Without Context

**Prompt:**
> "Fix the NullPointerException in my Java code. It crashes sometimes when processing user data."

**Response:**

To fix a NullPointerException when processing user data, here are common approaches:

1. **Add null checks before accessing objects:**
```java
if (user != null && user.getData() != null) {
    // process
}
```

2. **Use Optional:**
```java
Optional.ofNullable(user)
    .map(User::getData)
    .ifPresent(this::process);
```

3. **Add try-catch:**
```java
try {
    processUser(user);
} catch (NullPointerException e) {
    log.error("User data was null");
}
```

*Without seeing your code, I can't pinpoint the exact issue.*

**Score: 2/5**
- ❌ Cannot identify the actual line (43)
- ❌ Cannot identify `city` as the null value
- ⚠️ Generic Optional suggestion
- ❓ Unknown if API compatible
- ❓ Unknown about schema constraints

---

## ✅ With Context

**Prompt:**
```markdown
## Task
Fix the NullPointerException in this code.

## Code (UserService.java)
[Full code provided]

## Error Log
java.lang.NullPointerException at UserService.java:43
Caused by: null value for Address.city on userId=usr_38291

## Database Record
{"address": {"city": null}}

## Constraints
- Spring Boot 3.x, ~15% have null city
- Cannot change schema
- Team requires Optional-based null handling
```

**Response:**

The NPE is on **line 43**: `address.getCity().toUpperCase()` — the `city` field is `null` for ~15% of users.

**Fix (following team's Optional-based standards):**

```java
public UserProfile getProfile(String userId) {
    User user = userRepo.findById(userId);
    Address address = user.getAddress();
    
    String city = Optional.ofNullable(address)
        .map(Address::getCity)
        .map(String::toUpperCase)
        .orElse(null);  // null is acceptable per API contract
    
    notifier.sendWelcome(user.getEmail());
    return new UserProfile(user.getName(), city, user.getEmail());
}
```

**Why this works:**
- ✅ Uses Optional (team standard)
- ✅ Handles the 15% null-city cases
- ✅ Returns `null` for city (API contract allows it)
- ✅ No schema changes needed
- ✅ Backward compatible

**Score: 5/5**
- ✅ Identifies line 43 as the issue
- ✅ Identifies `city` as null (not `address`)
- ✅ Uses Optional per team standards
- ✅ Preserves API compatibility
- ✅ No schema changes

---

## 📊 Summary

| Metric | Without Context | With Context | Improvement |
|--------|-----------------|--------------|-------------|
| Score | 2/5 | 5/5 | **+150%** |
| Identifies root cause | ❌ | ✅ | - |
| Follows team standards | ❌ | ✅ | - |
| Production-ready fix | ❌ | ✅ | - |
| Iterations needed | ~3-5 | 1 | **-80%** |

**Conclusion:** Context injection transformed a generic, unusable response into a production-ready, constraint-aware solution in a single prompt.
