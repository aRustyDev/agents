# Software Development Team Conventions

This document defines all coding conventions, naming standards, and team practices for the software development team.

## Naming Conventions

### General Principles
- Use descriptive, self-documenting names
- Avoid abbreviations except well-known ones
- Be consistent within the codebase
- Prefer clarity over brevity

### Language-Specific Conventions

#### JavaScript/TypeScript
```javascript
// Classes: PascalCase
class UserAccount { }

// Interfaces: PascalCase with 'I' prefix (optional)
interface IUserService { }

// Functions/Methods: camelCase
function calculateTotal() { }

// Variables: camelCase
const userAge = 25;

// Constants: UPPER_SNAKE_CASE
const MAX_RETRY_COUNT = 3;

// Private members: underscore prefix
private _internalState;

// Files: kebab-case
user-service.ts
api-controller.js
```

#### Python
```python
# Classes: PascalCase
class UserAccount:
    pass

# Functions/Methods: snake_case
def calculate_total():
    pass

# Variables: snake_case
user_age = 25

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# Private members: underscore prefix
_internal_state = None

# Files: snake_case
user_service.py
api_controller.py
```

#### Java
```java
// Classes: PascalCase
public class UserAccount { }

// Interfaces: PascalCase
public interface UserService { }

// Methods: camelCase
public void calculateTotal() { }

// Variables: camelCase
int userAge = 25;

// Constants: UPPER_SNAKE_CASE
public static final int MAX_RETRY_COUNT = 3;

// Packages: lowercase
com.company.project.service

// Files: PascalCase (matching class name)
UserAccount.java
```

### Database Conventions
```sql
-- Tables: snake_case plural
CREATE TABLE users ( );
CREATE TABLE order_items ( );

-- Columns: snake_case
user_id INTEGER
created_at TIMESTAMP

-- Indexes: idx_table_column
CREATE INDEX idx_users_email ON users(email);

-- Foreign keys: fk_table_referenced
ALTER TABLE orders 
  ADD CONSTRAINT fk_orders_users 
  FOREIGN KEY (user_id) 
  REFERENCES users(id);
```

## Code Organization

### Project Structure
```
project-root/
├── src/
│   ├── components/     # Reusable components
│   ├── services/       # Business logic
│   ├── models/         # Data models
│   ├── utils/          # Utility functions
│   ├── config/         # Configuration files
│   └── types/          # Type definitions
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── docs/              # Documentation
├── scripts/           # Build/deployment scripts
└── README.md
```

### File Organization
1. Imports/Dependencies (sorted)
2. Constants/Configuration
3. Type definitions
4. Main class/function
5. Helper functions
6. Exports

### Module Structure
```javascript
// 1. Imports
import { calculateTax } from './utils';
import { User } from './models';

// 2. Constants
const TAX_RATE = 0.08;

// 3. Types
interface OrderItem {
  id: string;
  price: number;
}

// 4. Main functionality
export class OrderService {
  // Implementation
}

// 5. Helpers
function validateOrder(items: OrderItem[]): boolean {
  // Validation logic
}

// 6. Exports
export { validateOrder };
```

## Commit Message Conventions

### Format
```
type(scope): subject

body

footer
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting)
- **refactor**: Code refactoring
- **test**: Test additions/changes
- **chore**: Build process or auxiliary tool changes

### Example
```
feat(auth): implement two-factor authentication

DEVNOTES:
- Added TOTP generation using speakeasy library
- Implemented QR code generation for easy setup
- Added rate limiting to prevent brute force

LESSONS LEARNED:
- TOTP window should be at least 1 to handle clock drift
- QR codes should include issuer for better UX

REFERENCES:
- RFC 6238 for TOTP specification
- https://github.com/speakeasy/speakeasy-js

Closes #123
```

## Documentation Conventions

### Code Comments

#### Inline Comments
```javascript
// Calculate tax after applying discount
const finalPrice = basePrice * (1 - discount) * (1 + TAX_RATE);

// MOCKTHIS: External payment service
const paymentResult = await paymentService.process(order);

// UNTESTABLE: Hardware-dependent operation
const sensorReading = hardwareInterface.read();

// PUBLICFACING: This API is exposed to third parties
router.post('/api/v1/orders', createOrder);
```

#### Block Comments
```javascript
/**
 * DEVNOTES: Order processing implementation
 * - Validates order items against inventory
 * - Calculates pricing including taxes and discounts
 * - Processes payment through external gateway
 * - Updates inventory upon successful payment
 * - Sends confirmation email asynchronously
 * 
 * BUSINESSCASE: Core order fulfillment logic
 * - Ensures inventory availability before charging
 * - Applies business rules for pricing (bulk discounts, promotions)
 * - Maintains audit trail for compliance
 * - Handles partial fulfillment scenarios
 */
function processOrder(order: Order): Promise<OrderResult> {
  // Implementation
}
```

### API Documentation
```javascript
/**
 * Creates a new user account
 * 
 * @route POST /api/users
 * @param {Object} userData - User registration data
 * @param {string} userData.email - User's email address
 * @param {string} userData.password - User's password (min 8 chars)
 * @param {string} [userData.name] - User's display name
 * @returns {Object} User object with generated ID
 * @throws {ValidationError} If email is invalid or already exists
 * @throws {Error} If database operation fails
 * 
 * @example
 * const user = await createUser({
 *   email: 'user@example.com',
 *   password: 'securePass123',
 *   name: 'John Doe'
 * });
 */
```

## Testing Conventions

### Test File Naming
- Unit tests: `[module].test.[ext]`
- Integration tests: `[module].integration.test.[ext]`
- E2E tests: `[feature].e2e.test.[ext]`

### Test Structure
```javascript
describe('OrderService', () => {
  describe('calculateTotal', () => {
    it('should calculate total with tax', () => {
      // Arrange
      const items = [{ price: 100, quantity: 2 }];
      const taxRate = 0.08;
      
      // Act
      const total = calculateTotal(items, taxRate);
      
      // Assert
      expect(total).toBe(216); // 200 + 16 tax
    });
    
    it('should handle empty item list', () => {
      expect(calculateTotal([], 0.08)).toBe(0);
    });
    
    it('should throw error for negative prices', () => {
      const items = [{ price: -10, quantity: 1 }];
      expect(() => calculateTotal(items, 0.08)).toThrow('Invalid price');
    });
  });
});
```

### Test Data
```javascript
// Use factories for test data
const createTestUser = (overrides = {}) => ({
  id: 'test-id',
  email: 'test@example.com',
  name: 'Test User',
  ...overrides
});

// Use descriptive test data
const validCreditCard = '4242424242424242';
const expiredCreditCard = '4000000000000069';
const insufficientFundsCreditCard = '4000000000009995';
```

## Branch Naming Conventions

### Format
```
<type>/<ticket>-<description>
```

### Types
- **feature**: New functionality
- **fix**: Bug fixes
- **hotfix**: Urgent production fixes
- **refactor**: Code improvements
- **docs**: Documentation updates
- **test**: Test additions/updates
- **chore**: Maintenance tasks

### Examples
```
feature/PROJ-123-user-authentication
fix/PROJ-456-payment-calculation-error
hotfix/PROJ-789-critical-security-patch
refactor/PROJ-321-optimize-database-queries
docs/PROJ-654-api-documentation
```

## Error Handling Conventions

### Error Types
```javascript
// Custom error classes
class ValidationError extends Error {
  constructor(field, message) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

class BusinessRuleError extends Error {
  constructor(rule, message) {
    super(message);
    this.name = 'BusinessRuleError';
    this.rule = rule;
  }
}

class AuthenticationError extends Error {
  constructor(message = 'Authentication failed') {
    super(message);
    this.name = 'AuthenticationError';
  }
}
```

### Error Handling Pattern
```javascript
try {
  // Risky operation
  const result = await performOperation();
  return result;
} catch (error) {
  // Log error with context
  logger.error('Operation failed', {
    error: error.message,
    stack: error.stack,
    context: { userId, operation: 'performOperation' }
  });
  
  // Handle specific error types
  if (error instanceof ValidationError) {
    return res.status(400).json({
      error: 'Validation failed',
      field: error.field,
      message: error.message
    });
  }
  
  // Re-throw unexpected errors
  throw error;
}
```

## Logging Conventions

### Log Levels
- **ERROR**: System errors, exceptions
- **WARN**: Warnings, deprecated usage
- **INFO**: Important business events
- **DEBUG**: Detailed debugging information

### Log Format
```javascript
logger.info('User login successful', {
  userId: user.id,
  email: user.email,
  ip: request.ip,
  timestamp: new Date().toISOString()
});

logger.error('Payment processing failed', {
  orderId: order.id,
  amount: order.total,
  error: error.message,
  paymentGateway: 'stripe',
  timestamp: new Date().toISOString()
});
```

## Security Conventions

### Input Validation
```javascript
// Always validate input
const schema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  age: Joi.number().min(18).max(120)
});

const { error, value } = schema.validate(input);
if (error) {
  throw new ValidationError(error.details[0].path, error.message);
}
```

### Sensitive Data
```javascript
// Never log sensitive data
logger.info('User created', {
  userId: user.id,
  email: user.email
  // Do NOT log: password, ssn, creditCard, etc.
});

// Use environment variables for secrets
const apiKey = process.env.API_KEY;
const dbPassword = process.env.DB_PASSWORD;

// Sanitize output
const userResponse = {
  id: user.id,
  email: user.email,
  name: user.name
  // Exclude: password, salt, internal fields
};
```

## Performance Conventions

### Optimization Guidelines
1. Measure before optimizing
2. Optimize algorithms before micro-optimizations
3. Use appropriate data structures
4. Implement caching strategically
5. Batch operations when possible

### Caching Pattern
```javascript
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

async function getCachedData(key) {
  const cached = cache.get(key);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  
  const data = await fetchFromDatabase(key);
  cache.set(key, {
    data,
    timestamp: Date.now()
  });
  
  return data;
}
```

## Review Checklist

Before submitting code for review, ensure:

- [ ] All tests pass
- [ ] Coverage requirements met (100% functions)
- [ ] No linting errors
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow convention
- [ ] Branch naming follows pattern
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Error handling implemented