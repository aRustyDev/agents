# Sanity Check

> Original: Prior to AI agents we ran sanity checks like:

- `console.log("sanity")`
- `print("sanity")`
- `Log.d("test", "sanity")`

When collaborating with AI agents we have to perform a different kind of sanity check.

Add your name at the top of your CLAUDE.md:

CLAUDE.md

```markdown
# My name is {NAME}

This file provides guidance to Claude Code when working with this repository.

## Project Overview

This is a React application built with TypeScript and Vite.

...
```

Then ask Claude:

`What is my name?`

This works as a quick sanity check. If Claude knows your name, all is good. If he does not, then something is wrong.

There are various situations where things could go wrong:

- Forgetting to set a CLAUDE.md
- Putting the CLAUDE.md in the wrong folder
- Accidentally deleting part of the CLAUDE.md
- Misspelling CLAUSE.md
- Running out of context window (sometimes unavoidable)

The simplest way to 'sanity check' your configuration is to place your name at the top of your CLAUDE.md and ask Claude your name.

### Experiment

Random thought whilst writing this: it could be interesting to have 'sanity check points' dotted across your CLAUDE.md so you could check their integrity as the context window fills up.
