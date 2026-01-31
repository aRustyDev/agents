look in the REPLACE_THIS_BRANCH and find the last branch that was created from it with the name pattern WIP-*

Take the commit that branch was created from and the current head of REPLACE_THIS_BRANCH.

analyze the chain of commits in between the branches origin and the head, and create an estimate of how long the work for all the changes involved would take a normal developer without ai tools, assuming it is just one developer and not a team effort.
Use that estimate to plan out a schedule of when each of those portions of code would have been deliverved.

output the resulting plan in json format to `.changelog/schedule/work.json`. 
The outputted json should include the following
1. The commit sha
2. The date that the work would be delivered
3. The estimated work hours involved to complete it
4. The diff of the values of the `.changelog/commit/notes`
