start by identifying the feature or function to be tested and define its objective. Then, create detailed test steps, including preconditions, and specify the expected results. Ensure test cases are clear, concise, and reusable, using unique IDs and proper formatting. Finally, consider automating tests and collaborating with developers


Understand the Requirements and Scope:

    Analyze the specifications:
    Thoroughly review the requirements documents, user stories, and design specifications to understand the functionality and intended behavior of the software. 

Identify test scenarios:
Determine the different ways the software can be used and the potential scenarios that need to be tested. 
Define the test objective:
Clearly state what the test case aims to achieve and what aspect of the software is being verified. 

2. Structure the Test Case:

    Test Case ID: Assign a unique identifier to each test case for easy tracking and reference. 

Title: Give the test case a descriptive and concise title that clearly indicates the functionality being tested. 
Description: Provide a clear and concise explanation of the test case's purpose and the scenario it covers. 
Preconditions: Specify any conditions that must be met before the test case can be executed. 
Test Steps: Detail the steps required to execute the test case in a clear and sequential manner. 
Expected Results: Clearly state the expected outcome of each step and the overall test case. 
Actual Results: After execution, record the actual outcome of the test. 
Status: Indicate whether the test case passed, failed, or was blocked. 
Test Data: Include any necessary input data required for the test case. 
Environment: Specify the testing environment (e.g., browser, operating system). 
Notes: Add any additional information or observations. 

3. Best Practices for Writing Test Cases:

    Keep it simple and clear: Use plain language that is easy to understand and follow. 

Be concise: Avoid unnecessary details and focus on the core functionality. 
Be specific: Avoid ambiguity and ensure that the expected results are clearly defined. 
Cover positive and negative scenarios: Test both expected behavior and potential errors. 
Make test cases reusable: Design tests that can be easily adapted for different situations. 
Consider automation: Identify test cases that can be automated to save time and effort. 
Prioritize test cases: Focus on the most critical functionality and potential risks. 
Review test cases: Have other team members review your test cases to ensure clarity and accuracy. 

4. Example:
Let's say you're testing a login feature: 

    Test Case ID: TC_LOGIN_001
    Title: Verify successful login with valid credentials
    Description: This test case verifies that a user can successfully log in to the application using a valid username and password.
    Preconditions: User account must exist.
    Test Steps:
        Navigate to the login page.
        Enter a valid username.
        Enter a valid password.
        Click on the login button. 
    Expected Results: User should be redirected to the application's home page.
    Actual Results: (To be filled after execution)
    Status: (To be filled after execution)
    Test Data: Username: "testuser", Password: "password"
    Environment: Chrome browser on Windows 10.


 if a test is trying to use a function that is missing, not simply misnamed, then analyze the target code and the tests use case to determine if the test is       │
│   trying to test something it doesn't need too. If the test is trying to test something unneccesary try removing whatever is calling the missing method from the    │
│   test, or remove the test entirely.

---

# Updating CLAUDE.md

After successfully creating a complete test. Update the `## Testing` section of CLAUDE.md with the following information
- Total Tests
- Passing Tests
- Failing Tests
- Test Execution Time
- Code Coverage Stats
    - % Statements covered
    - % Lines Covered
    - % Modules Covered
    - % Classes Covered
    - % Methods Covered (standalone only)
- Test Case Stats (Want to capture robustness)
    - Test Cases Total
    - Test Cases Per Test Average
    - Perfectly Normal Case (all tests have same # test cases)

---

## Making your Case
- Analyze the code in question
- Analyze the dependents of that code and how the code in question affects the code.
- Analyze the codes dependencies and how the code in question is affected by it.
- Explore and analyze the best practices in regards to the code in question.
- Determine AT LEAST 1 alternative solution, IDEALLY 3 alternative solutions, and AT MOST 10 alternative solutions
- Determine the pros and cons of each solution, including the current implementation
- Provide in a prompt the alternatives in an abstract pattern based way with the pros and cons of each
- Iteratively collaborate with me to find the best solution, asking for additional clarification and input whenever you feel it useful or necessary.

---

## Testing

### How to get test results

- When updating CLAUDE.md: Run tests module by module like `python -m pytest tests/test_module_name.py --tb=no -q`
- After making a change to the code base or to test code: Run only the tests that are related to what you changed.
- 
---

> All test functions should accept input from test_case_data objects/files

# Prioritized Goals
1. **Accurate Numbers**: You MUST NEVER inflate or misrepresent the tests passed or failed. It is ALWAYS better to be honest and tell the truth, being dishonest or unfactual will result in our collaboration failing. In every representation of the tests current pass/fail rate, be sure to specify the current state for ALL tests, and then annotate how many of those tests were the subject of work we focused on, and then describe the state of that subset of test results before and after our work.
2. **Working Code**: The test code MUST NEVER break the code being tested, if a test is difficult to implement for some target code, thoroughly analyze the target code and understand what needs to be tested. Next if your analysis determined that the target code is suitably complex to test, the prompt me with the issue and iteratively provide potential strategies and example implementations of the target code that would retain its functionality while simplifying the code needed to test it.
3. **Maintainable Code**: 
4. **Well Implemented Tests**: Just because a test works doesn't mean its good. If a test is just passing all tests without validating something then its a bad test. Tests should validate either business or application logic, or they should test unit functionality, both are important. Tests should ideally be able to accept mock providers, and function as if they were the target code, instead of a restatement of the target code.
5. **Maintainable/Reusable Tests**: Tests should be able to share test case data, and test case data should be representative of real world examples including user error, machine error, or malicious intent. Tests should not be 'brittle' or be quick to require updates as the target code is changed.
6. **Working Tests**: No test should exist that tries to test code that doesn't exist. By default, tests should take a black-box testing approach, concerned primarily with testing the target codes functionality and behavior. If a test is created as a placeholder, it should be annotated with internal comments describing what it is meant to test, and why it has not been implemented.
7. **Passing Tests**
8. **Test Coverage**

## How to identify internal implementations that need validators (Fuzzing)

## How to identify internal implementations that need tests

## How to identify code that needs to be mocked

- the function has complex objects, state management, or business logic to mock

1. Explore the test code, highlight any tests that are attempting to test internal implementation details rather than functionality
2. Explore the tested code, identify any interfaces that should be tested, and would need to a test to be written for the implementation and not the functionality of the code
3. Unless the target code meets one of the exceptions mentioned in number 2, write tests for the target code that take a black-box testing approach, focused only on testing the expected behavior.
4. If the target code is a specific interface, add that interface as a testcase to the interface testing factory.
5. If the target code is an internal validator, add a test to fuzz the validator and ensure the logic is working as expected and robust enough to catch edge cases. Be hesitant to test internal validators, if you find one, prompt me with an alternative utility function that can be abstracted for reuse in other methods. Only if I tell you to test the internal validator should you do it.

review the modules and analyze them for unnecessary tests, inaccurate return type or method attribute expectations, poor or unnecessary mocking approaches, tests that target non-existent functions, and tests that are trying to test implementation details instead of code behaviour/functionality or business logic.
---
