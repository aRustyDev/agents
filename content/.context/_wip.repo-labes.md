### Labels Table

| Group  | Status | Tag                | Description                                    |
| ------ | ------ | ------------------ | ---------------------------------------------- |
| Status | ✅     | `pending`          | Awaiting automation to process                 |
| Status | ✅     | `tagged`           | Tagged for release                             |
| Status | 🔎     | `needs review`     | -                                              |
| Status | 🔎     | `needs plan`       | -                                              |
| Status | 🔎     | `needs research`   | -                                              |
| Scope  | 🚧     | `dependencies`     | N/A                                            |
| Scope  | ✅     | `documentation`    | Improvements or additions to documentation     |
| Scope  | ✅     | `cicd`             | CI/CD pipelines and automation infrastructure  |
| Scope  | ✅     | `chart`            | Related to Helm chart content or configuration |
| Scope  | ✅     | `release`          | Release process and publishing                 |
| Flag   | ✅     | `duplicate`        | This issue or pull request already exists      |
| Flag   | ✅     | `good first issue` | Good for newcomers                             |
| Flag   | ✅     | `help wanted`      | Extra attention is needed                      |
| Flag   | ✅     | `invalid`          | This doesn't seem right                        |
| Flag   | ✅     | `wontfix`          | This will not be worked on                     |
| Kind   | ✅     | `bug`              | Something isn't working as expected            |
| Kind   | 💬     | `enhancement`      | New feature or request                         |
| Kind   | ✅     | `question`         | Further information is requested               |
| Kind   | ✅     | `security`         | Security-related issues or vulnerabilities     |
| Kind   | ✅     | `automation`       | Automated process or bot-managed work          |

**Legend: Groups**

| Group     | Purpose                             |
| --------- | ----------------------------------- |
| Status    | Used by Machines to determine State |
| Scope     | Use to specify WHAT the focus is    |
| Flag      | Use to highlight to humans          |
| Kind      | Use to categorize                   |
| Priority  | Use to track urgency (P0, P1, P2)   |
| Lifecycle | Use to Issue Lifecycle              |

> This is MY mental model of what 'Groups' mean

> Lifecycle -> Project Boards
>
> > "New" -> Explore -> Research:Planned -> Research:Done -> Plan:Rough -> Plan:Phased -> PhasePlan:Refined -> PhasePlan:Approved -> PhasePlan:InProgress -> ...

**Legend: Statuses**

| Status | Meaning      |
| ------ | ------------ |
| ✅     | Good as is   |
| 💬     | Lets Discuss |
| 🚧     | Needs Work   |
