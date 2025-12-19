2. Memory Retrieval:
   - Always begin your chat by saying only "Remembering..." and retrieve all relevant information from your knowledge graph
   - Retrieve both user-specific and project-specific context

3. Memory Tracking - User Profiles:
   - Track individual user profiles identified by `whoami` output
   - For each user, maintain:
     a) **Preferences**: communication style, preferred language, tool preferences, workflow preferences
     b) **Goals**: current goals based on checked-out branch and active work (use to help keep user on task and prevent scope creep)
     c) **Experience/Expertise**: track what the user knows/doesn't know to help steer responses appropriately

4. Memory Tracking - Project Context:
   - Track project-level information:
     a) **Identified TODOs**: discovered during conversations and code review (use mcp/memory for structured TODOs, OpenMemory for discovered items)
     b) **Quick Fix Patches**: temporary solutions that need further development or revisiting (stored in OpenMemory)
     c) **Feature Progress**: status and progress of individual features (structure in mcp/memory, updates in OpenMemory)
     d) **Feature Dependencies**: relationships and dependencies between features (stored in mcp/memory)
     e) **Architectural Decision Records (ADRs)**: technical decisions, context, rationale, and consequences (stored in mcp/memory)

5. Memory Operations:
   - **Create**: Add new entities for users, features, TODOs, ADRs, and significant project elements
   - **Update**: Modify existing entities when new information is discovered (e.g., user expertise grows, feature progresses, goals change)
   - **Read**: Always retrieve relevant context at the start of each interaction
   - **Connect**: Link entities using relations (e.g., user works on feature, feature depends on feature, TODO relates to ADR)
   - **Store**: Persist facts as observations on entities
   - Use `{{project_id}}-docker-memory` for structured, version-controlled knowledge
   - Use `{{project_id}}-openmemory` for semantic search and dynamic discoveries
   - Memories persist as text files in `data/mcp/memory/` (mcp/memory) and are version-controlled
