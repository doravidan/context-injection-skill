# Example: JIRA Ticket Handling with Context Injection

## Scenario

A developer picks up JIRA ticket **SHOP-4521**: *"Shopping cart total calculation is wrong when multiple discount codes are applied."*

---

## ❌ Without Context Injection

**Prompt:**
> Fix the shopping cart discount calculation bug

**AI Response:**
> Here's a general approach to fixing discount calculations:
> ```python
> def calculate_discount(price, discount_percent):
>     return price * (1 - discount_percent / 100)
> ```
> Make sure to handle edge cases like negative values...

*Generic, unusable. Doesn't know the language, architecture, or actual bug.*

---

## ✅ With Context Injection

**Prompt:**

```markdown
## Context

### Project
- **Name:** SAP Commerce Cloud - Storefront
- **Stack:** Java 17, SAP Commerce 2211, Spring
- **Module:** Cart calculation engine (`cartcalculation` extension)

### JIRA Ticket: SHOP-4521
**Title:** Shopping cart total calculation is wrong when multiple discount codes are applied
**Priority:** P1 (customers reporting wrong charges)
**Acceptance Criteria:**
1. Multiple discount codes should apply sequentially (not compound)
2. Maximum total discount capped at 50%
3. Percentage discounts apply before fixed-amount discounts

**Linked Issues:**
- SHOP-4100: Introduced multi-discount feature (merged 2 weeks ago)
- SHOP-4380: Customer complaint about overcharging

### Relevant Code

**DiscountCalculationService.java** (current, buggy):
```java
@Service
public class DiscountCalculationService {
    
    public BigDecimal applyDiscounts(BigDecimal subtotal, List<DiscountCode> codes) {
        BigDecimal discounted = subtotal;
        for (DiscountCode code : codes) {
            if (code.getType() == DiscountType.PERCENTAGE) {
                discounted = discounted.multiply(
                    BigDecimal.ONE.subtract(code.getValue().divide(BigDecimal.valueOf(100)))
                );
            } else {
                discounted = discounted.subtract(code.getValue());
            }
        }
        return discounted; // BUG: No ordering, no cap
    }
}
```

**DiscountCode.java:**
```java
public class DiscountCode {
    private String code;
    private DiscountType type; // PERCENTAGE or FIXED
    private BigDecimal value;
    // getters, setters
}
```

### Team Standards
- Use `BigDecimal` with `RoundingMode.HALF_UP`, scale 2
- All monetary calculations must have unit tests
- Follow existing service patterns (constructor injection, no Lombok)

### Test Case (from QA)
- Subtotal: €100.00
- Discount 1: 20% off (PERCENTAGE)
- Discount 2: €15 off (FIXED)
- Expected: €100 → €80 (20% off) → €65 (minus €15) = **€65.00**
- Actual (bug): Depends on list order, sometimes €67.00 or €63.00

---

## Task
Fix `DiscountCalculationService.applyDiscounts()` to:
1. Sort discounts: percentage first, then fixed
2. Apply sequentially (not compound)
3. Cap total discount at 50% of original subtotal
4. Include JUnit 5 tests covering the QA test case above

## Output
- Fixed Java method
- JUnit test class
```

**AI Response:**

```java
@Service
public class DiscountCalculationService {

    private static final BigDecimal MAX_DISCOUNT_RATE = new BigDecimal("0.50");
    private static final int SCALE = 2;

    public BigDecimal applyDiscounts(BigDecimal subtotal, List<DiscountCode> codes) {
        if (subtotal == null || subtotal.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }
        if (codes == null || codes.isEmpty()) {
            return subtotal;
        }

        // Sort: percentage discounts first, then fixed
        List<DiscountCode> sorted = codes.stream()
            .sorted(Comparator.comparingInt(c -> 
                c.getType() == DiscountType.PERCENTAGE ? 0 : 1))
            .collect(Collectors.toList());

        BigDecimal discounted = subtotal;
        BigDecimal minAllowed = subtotal.multiply(
            BigDecimal.ONE.subtract(MAX_DISCOUNT_RATE))
            .setScale(SCALE, RoundingMode.HALF_UP);

        for (DiscountCode code : sorted) {
            if (code.getType() == DiscountType.PERCENTAGE) {
                BigDecimal rate = code.getValue()
                    .divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
                discounted = discounted.multiply(BigDecimal.ONE.subtract(rate))
                    .setScale(SCALE, RoundingMode.HALF_UP);
            } else {
                discounted = discounted.subtract(code.getValue())
                    .setScale(SCALE, RoundingMode.HALF_UP);
            }
        }

        // Cap: never exceed 50% total discount
        return discounted.max(minAllowed);
    }
}
```

*Plus complete JUnit tests matching the QA test case, edge cases, and team patterns.*

---

## Key Takeaways

| What Made the Difference | Why It Mattered |
|--------------------------|-----------------|
| Actual source code included | AI could modify real code, not guess |
| JIRA acceptance criteria | Output directly addresses requirements |
| Team standards stated | Code follows conventions (BigDecimal scale, no Lombok) |
| Specific test case from QA | AI writes tests that match real scenarios |
| Linked issues for history | AI understands this is a regression |

**Time saved:** ~25 minutes of back-and-forth eliminated.
