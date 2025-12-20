---
name: Behavior-Driven Development Pattern
module_type: pattern
scope: context
priority: medium
triggers: ["BDD", "behavior driven", "behavior-driven development", "gherkin", "cucumber", "given when then"]
dependencies: ["core/principles.md", "processes/testing/acceptance-testing.md"]
conflicts: ["patterns/development/tdd-pattern.md", "patterns/development/cdd-pattern.md"]
version: 1.0.0
---

# Behavior-Driven Development (BDD) Pattern

## Purpose
Develop software by defining behavior through examples written in business-readable language. BDD bridges the gap between technical and non-technical stakeholders by using structured natural language to describe system behavior.

## Core Principles

1. **Shared Understanding**: Common language for all stakeholders
2. **Living Documentation**: Executable specifications
3. **Outside-In Development**: Start from user perspective
4. **Example-Driven**: Concrete scenarios over abstract requirements
5. **Collaboration First**: Three Amigos approach (Business, Development, Testing)

## Implementation

### Overview
BDD uses a structured format (Given-When-Then) to describe behavior scenarios. These scenarios serve as automated tests, documentation, and communication tools between stakeholders.

### Rules

#### Scenario Writing Rules
1. **Use business language**
   - Avoid technical jargon
   - Focus on what, not how
   - Use domain terminology

2. **Follow Given-When-Then format**
   - **Given**: Initial context/state
   - **When**: Action or event
   - **Then**: Expected outcome
   - **And/But**: Additional steps

3. **Keep scenarios focused**
   - One behavior per scenario
   - Clear success criteria
   - Independent scenarios

4. **Make scenarios concrete**
   - Use specific examples
   - Avoid vague descriptions
   - Include real data

#### Development Rules
1. **Start with scenarios**
   - Write scenarios before code
   - Get stakeholder agreement
   - Define acceptance criteria

2. **Automate scenarios**
   - Map to step definitions
   - Keep steps reusable
   - Maintain readability

3. **Implement outside-in**
   - Start with UI/API layer
   - Work down to domain
   - Mock external dependencies

### Scenario Format

```gherkin
Feature: Shopping Cart Management
  As a customer
  I want to manage items in my cart
  So that I can purchase multiple products

  Background:
    Given the following products exist:
      | name        | price  | stock |
      | Laptop      | 999.99 | 10    |
      | Mouse       | 29.99  | 50    |
      | Keyboard    | 79.99  | 30    |

  Scenario: Add item to empty cart
    Given I am a logged-in customer
    And my shopping cart is empty
    When I add 1 "Laptop" to my cart
    Then my cart should contain 1 item
    And the cart total should be $999.99

  Scenario: Apply discount code
    Given I have the following items in my cart:
      | product  | quantity |
      | Laptop   | 1        |
      | Mouse    | 2        |
    When I apply the discount code "SAVE10"
    Then a 10% discount should be applied
    And the cart total should be $965.98

  Scenario Outline: Stock validation
    Given I am viewing the "<product>" page
    And there are <available> items in stock
    When I try to add <requested> items to my cart
    Then I should <result>

    Examples:
      | product  | available | requested | result                    |
      | Laptop   | 5         | 3         | see 3 items in my cart   |
      | Laptop   | 2         | 5         | see an out of stock error |
      | Mouse    | 0         | 1         | see an out of stock error |
```

### Step Implementation

```python
# Step definitions (Python with behave)
from behave import given, when, then
from hamcrest import assert_that, equal_to, has_length

@given('I am a logged-in customer')
def step_logged_in_customer(context):
    context.user = User.create_test_user()
    context.session = Session.login(context.user)

@given('my shopping cart is empty')
def step_empty_cart(context):
    context.cart = ShoppingCart(context.session)
    context.cart.clear()

@when('I add {quantity:d} "{product}" to my cart')
def step_add_to_cart(context, quantity, product):
    item = Product.find_by_name(product)
    context.result = context.cart.add_item(item, quantity)

@then('my cart should contain {count:d} item')
def step_verify_cart_count(context, count):
    assert_that(context.cart.items, has_length(count))

@then('the cart total should be ${amount:f}')
def step_verify_cart_total(context, amount):
    assert_that(context.cart.calculate_total(), equal_to(amount))
```

### Three Amigos Sessions

Before writing scenarios, hold collaborative sessions:

1. **Business Representative**: Defines value and acceptance
2. **Developer**: Assesses feasibility and approach
3. **Tester**: Identifies edge cases and scenarios

Example conversation:
```
Business: "We need a discount system for bulk orders"
Developer: "What qualifies as bulk?"
Tester: "What if they add items after discount?"
Business: "Over 10 items gets 10% off"
Developer: "Applied at checkout or in cart?"
Tester: "Can discounts stack?"
→ Results in clear, agreed scenarios
```

## When to Apply

### Ideal Scenarios
- **Complex business logic**: Where domain understanding crucial
- **Multi-stakeholder projects**: Need shared understanding
- **Regulatory requirements**: Compliance needs documentation
- **API development**: Clear contract definition
- **User-facing features**: Focus on user value

### Not Recommended For
- **Technical infrastructure**: Low-level implementation
- **Algorithmic code**: Mathematical computations
- **Prototypes**: When requirements unstable
- **Solo projects**: Overhead without collaboration

## Benefits

- **Clear communication**: Reduces misunderstandings
- **Living documentation**: Always up-to-date
- **Automated acceptance tests**: Confidence in delivery
- **Shared ownership**: Everyone understands system
- **Focus on value**: User-centric development

## Trade-offs

### Advantages
- ✅ Stakeholder collaboration
- ✅ Clear acceptance criteria
- ✅ Executable documentation
- ✅ Reduces rework
- ✅ Better requirement understanding

### Disadvantages
- ❌ Initial overhead
- ❌ Requires stakeholder commitment
- ❌ Maintenance of scenarios
- ❌ Tool complexity
- ❌ Translation layer needed

## Anti-Patterns

### Technical Scenarios
❌ Using implementation details in scenarios
```gherkin
# Bad
When I execute SQL query "SELECT * FROM users"
Then the ResultSet should have 3 rows
```

✅ Focus on business behavior
```gherkin
# Good
When I search for active users
Then I should see 3 users in the results
```

### Imperative Style
❌ UI-level step-by-step instructions
```gherkin
# Bad
When I click the "Login" button
And I type "user@example.com" in the "Email" field
And I type "password123" in the "Password" field
And I click the "Submit" button
```

✅ Declarative business actions
```gherkin
# Good
When I log in with valid credentials
```

### Scenario Explosion
❌ Testing every permutation
✅ Focus on key examples and edge cases

### Developer-Only BDD
❌ Writing scenarios without stakeholder input
✅ Collaborative scenario development

## Integration

### With Development Workflow
```
1. Three Amigos Session
   ↓
2. Write Scenarios
   ↓
3. Get Stakeholder Sign-off
   ↓
4. Automate Scenarios (Red)
   ↓
5. Implement Feature (Green)
   ↓
6. Refactor
   ↓
7. Demo with Scenarios
```

### With CI/CD
```yaml
# Example GitHub Actions
bdd-tests:
  steps:
    - name: Run BDD Tests
      run: |
        behave features/ --junit --junit-directory reports/
        cucumber-js --format json:reports/cucumber.json
    
    - name: Publish Reports
      uses: cucumber/publish-action@v1
      with:
        cucumber-messages: reports/
```

## Tooling

### BDD Frameworks by Language
- **Ruby**: Cucumber, RSpec
- **Python**: behave, pytest-bdd
- **JavaScript**: Cucumber.js, Jest-Cucumber
- **Java**: Cucumber-JVM, JBehave
- **C#**: SpecFlow, NSpec

### Supporting Tools
- **Gherkin**: Scenario language
- **Pickle**: Gherkin parser
- **Allure**: Test reporting
- **Living Doc**: Documentation generation

## Scenario Patterns

### Basic CRUD Pattern
```gherkin
Feature: Article Management

Scenario: Create article
  Given I am an authenticated author
  When I create an article with title "BDD Benefits"
  Then the article should be saved
  And I should see it in my article list

Scenario: Update article
  Given I have an article titled "Draft Post"
  When I update the title to "Published Post"
  Then the article title should be "Published Post"
```

### State Transition Pattern
```gherkin
Scenario: Order fulfillment workflow
  Given an order in "pending" status
  When I mark the order as "shipped"
  Then the order status should be "shipped"
  And the customer should receive a shipping notification
```

### Business Rule Pattern
```gherkin
Scenario: Free shipping qualification
  Given the minimum for free shipping is $50
  When I have $45 worth of items in my cart
  Then I should see "Add $5 more for free shipping"
  
  When I add a $10 item to my cart
  Then I should see "You qualify for free shipping"
```

## Migration Strategy

### From Requirements to BDD
1. Identify key user stories
2. Run Three Amigos for each story
3. Convert acceptance criteria to scenarios
4. Gradually build scenario library
5. Retire old requirement docs

### From BDD to TDD
- BDD defines the "what" (behavior)
- TDD implements the "how" (units)
- Use BDD for acceptance tests
- Use TDD for unit tests
- Both can coexist effectively

---
*Behavior-Driven Development transforms requirements into living documentation that drives development and ensures delivered software matches stakeholder expectations.*