create a plan to generate a prompt
The prompt MUST include the requirements specified in REQUIRED.md.
The generated prompt MUST comply with the requirements specified in REQUIRED.md.
The generated prompt MUST create or update an mdbook
- User input
- Contextual information
- Constraints


Make sure that the prompt will output its understanding of each module there, understanding that it is part of a mdbook.Make sure the output addresses gooses functionality in a top down manner, explaining how each module is related to the others, how each module fits into goose, what the business function of each modules is, and then inside of each module explain how each class, method, function, or statement is related to each other and how they allfit together to make the module function. Additionally include each functions business use case, and where ever possible create and include mermaid diagrams or UMLdiagrams depicting the logical flows, relationships, sequences, or class diagrams, ensuring that any diagrams as code can be rendered in a gitlab hosted markdown file.

  1. Mermaid Diagrams:
    - Architecture overviews
    - Sequence diagrams for workflows
    - Class diagrams for structure
    - State diagrams for processes
  2. Business Context: Each module documented with:
    - Primary business purpose
    - Use cases in incident response
    - Integration with other modules
  3. Technical Details:
    - Function signatures and purposes
    - Error handling patterns
    - Performance considerations
    - Security implications
  4. Practical Guidance:
    - Common issues and solutions
    - Testing approaches
    - Integration guidelines
    - Future enhancement suggestions

References to strategy should include links to the code where applicable. for example.
```markdown
- Exponential backoff for rate limiting ([429 errors](path/to/source/this/refers/to))
- Comprehensive logging at multiple levels ([<LogLibraryUsed>](https://github.com/logrus/logrus))
- Graceful degradation ([continue on partial failures](path/to/source/this/refers/to))
- [State persistence](path/to/source/this/refers/to) for resumable operations
```
