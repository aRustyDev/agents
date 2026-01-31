 Mutation testing
https://dev.to/antoinecoulon/dont-target-100-coverage-387o

Regression Testing

Path Coverage: Path coverage is a more advanced type of test coverage that ensures every possible path through a given part of the code has been executed. This includes all possible combinations of branches.
  - Example: For a nested if-else statement, path coverage would ensure every possible sequence of decisions is tested.

Statement Coverage: This technique measures the percentage of executable statements in code that are executed at least once during testing. While a high statement coverage indicates thorough testing, it doesn't guarantee all functionalities or logic paths are exercised.
Statement Coverage Statement coverage refers to the percentage of individual statements in the code that have been executed during testing. If a test suite covers 80% statement coverage, it means 80% of the code’s lines or statements have been executed at least once.
  - Example: In the code if (x > 10) { print(x); }, both the condition and the print statement need to be executed to achieve 100% statement coverage.

Branch Coverage: This approach delves deeper than statement coverage. Branch coverage analyzes the percentage of conditional branch statements (if/else statements) where both the true and false paths are executed by test cases. This ensures that coverage tests explore different decision-making scenarios within the code.
Branch Coverage Branch coverage measures the extent to which different branches (true/false outcomes) of decision points (such as if statements) are tested. It ensures that both possible outcomes of each branch are covered.
  - Example: For the statement if (x > 10) { print(x); } else { print(“Small”); }, branch coverage requires that both the if and else branches are executed at least once.

Function Coverage: Function coverage focuses on the percentage of functions within the codebase that are invoked during testing. This technique helps identify functions that haven't been exercised and might harbor potential bugs.
Function Coverage: Function coverage tracks whether each function or method in the code has been executed during testing. It ensures that all individual functions are tested.

Decision Coverage: This technique builds on branch coverage, focusing on the logical combinations of conditions within decision statements. It ensures your tests explore all possible outcomes based on different input combinations.

Condition Coverage: Taking the analysis a step further, condition coverage measures the percentage of individual conditions within decision statements that are evaluated as true and false during testing. This provides a granular view of how thoroughly tests exercise the code's conditional logic.
Condition Coverage: Condition coverage ensures that each individual condition in a complex logical expression (e.g., && or ||) has been evaluated to both true and false at least once.

---
Untestable Code: Certain code sections, like error handling routines or initialization blocks, may be difficult or unnecessary to test in a direct manner. Focus efforts on core functionalities and decision-making logic.

Logic Errors: Even with high coverage, test suites might miss logic errors that don't manifest within the tested scenarios. Code reviews and exploratory testing techniques can help complement coverage testing.

Edge Cases and User Behavior: Coverage testing focuses on the code itself, but real-world user behavior can be unpredictable. Complement coverage testing with user acceptance testing and exploratory testing to uncover edge cases and unexpected user interactions.
---

1. Aim for Meaningful Coverage, Not Just High Numbers

While 100% test coverage sounds ideal, it is often not practical or necessary. Instead of obsessing over numbers, focus on testing the critical paths, edge cases, and high-risk areas of your code. A balanced approach ensures you’re testing what matters most.

2. Use Coverage Tools

Implement coverage tools like Istanbul (for JavaScript), JaCoCo (for Java), or Coverage.py (for Python) to automate the process of measuring test coverage. These tools will help you visualize which parts of your code are untested and can provide insights into improving your test suite.

3. Incorporate Unit Testing and Integration Testing

Unit tests validate individual components, while integration tests ensure that these components work together as expected. By combining both, you can achieve broader coverage and test how modules interact within the system.

4. Practice Test-Driven Development (TDD)

Test-driven development is a software development approach where you write tests before writing the actual code. This ensures that you write only the necessary code to pass the test, leading to better test coverage and cleaner code.

    Actionable Tip: Set a rule to write unit tests for every new feature or module before starting its implementation. This forces developers to think through edge cases and functionality beforehand.

5. Leverage AI for Test Generation

Use AI-generated tests to automatically create test cases based on historical code patterns, bug reports, or real-world usage. Tools like Keploy or Testim can analyze your code and generate meaningful test cases, improving coverage.

Set Coverage Targets
Establish minimum test coverage thresholds. For example, aim for at least 80% statement coverage and 70% branch coverage. These targets can be adjusted based on your project’s needs.


How to use constrained-random stimuli?

Constrained-random stimuli are test inputs that are generated randomly within a set of constraints defined by the verification engineer. The constraints can be based on the design specification, the test plan, or the functional coverage model. Constrained-random stimuli can help you explore a large and diverse space of scenarios, expose corner cases and bugs, and reduce the manual effort of writing directed tests. However, constrained-random stimuli also require careful planning, validation, and debugging to ensure that they are effective and relevant.

How to create a functional coverage model?

A functional coverage model is a representation of the design functionality and scenarios that need to be verified. It can be expressed in terms of coverpoints, bins, crosses, and covergroups, using a language such as SystemVerilog or e. A functional coverage model can help you define your verification objectives, track your verification progress, and identify gaps and redundancies in your testbench. A functional coverage model should be aligned with the design specification and the test plan, and should be updated and refined throughout the verification cycle.

How to use coverage feedback?

Coverage feedback is the process of using the coverage metrics to guide and optimize the verification process. Coverage feedback can help you adjust your testbench parameters, prioritize your test scenarios, and focus your verification resources and time on the areas that need more attention. Coverage feedback can also help you identify and eliminate unnecessary or ineffective tests, and achieve your verification closure criteria. Coverage feedback can be performed manually or automatically, using tools such as coverage analyzers, coverage-driven test generators, and coverage closure tools.

How to improve your coverage quality?

Coverage quality is the degree to which your coverage metrics reflect the true verification status of your design. This can be affected by the accuracy and completeness of your functional coverage model, the relevance and diversity of your constrained-random stimuli, and the robustness and observability of your testbench. To improve coverage quality, you should review and validate your functional coverage model regularly, use cross-coverage to capture complex interactions and dependencies, use assertions and checkers to verify the design behavior and outputs, use coverage exclusions and waivers to handle unverifiable or irrelevant code or functionality, and use coverage reports and reviews to evaluate and improve your coverage metrics.

Focus on Critical Areas - Prioritize achieving high coverage for core functionalities and areas with high user impact. These sections hold the most significant risk if defects remain undetected.
Integrate with CI/CD Pipelines - Incorporate coverage testing into your continuous integration and continuous delivery (CI/CD) pipelines. This ensures coverage reports are generated and reviewed with every build, enabling early identification of regressions.
Promote Collaboration - Encourage communication and collaboration between developers and testers. Developers can leverage coverage reports to identify areas for code improvement, while testers can use this information to focus their test case development efforts.
Data-Driven Testing for Comprehensive Coverage
Tests-Case Creation
