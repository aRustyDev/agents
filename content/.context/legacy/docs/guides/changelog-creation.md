# Keep a Changelog

> Don’t let your friends dump git logs into changelogs.
> Version 1.1.0

## [Example Changelog](../examples/changelog.md)

## What is a changelog?

A changelog is a file which contains a curated, chronologically ordered list of notable changes for each version of a project.
Why keep a changelog?

To make it easier for users and contributors to see precisely what notable changes have been made between each release (or version) of the project.

## Who needs a changelog?

People do. Whether consumers or developers, the end users of software are human beings who care about what's in the software. When the software changes, people want to know why and how.
How do I make a good changelog?

### Guiding Principles

- Changelogs are for humans, not machines.
- There should be an entry for every single version.
- The same types of changes should be grouped.
- Versions and sections should be linkable.
- The latest version comes first.
- The release date of each version is displayed.
- Mention whether you follow Semantic Versioning.

### Types of changes

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

### How can I reduce the effort required to maintain a changelog?

Keep an Unreleased section at the top to track upcoming changes.

This serves two purposes:

- People can see what changes they might expect in upcoming releases
- At release time, you can move the Unreleased section changes into a new release version section.

### Can changelogs be bad?

Yes. Here are a few ways they can be less than useful.

#### Commit log diffs

Using commit log diffs as changelogs is a bad idea: they're full of noise. Things like merge commits, commits with obscure titles, documentation changes, etc.

The purpose of a commit is to document a step in the evolution of the source code. Some projects clean up commits, some don't.

The purpose of a changelog entry is to document the noteworthy difference, often across multiple commits, to communicate them clearly to end users.

#### Ignoring Deprecations

When people upgrade from one version to another, it should be painfully clear when something will break. It should be possible to upgrade to a version that lists deprecations, remove what's deprecated, then upgrade to the version where the deprecations become removals.

If you do nothing else, list deprecations, removals, and any breaking changes in your changelog.

#### Confusing Dates

Regional date formats vary throughout the world and it's often difficult to find a human-friendly date format that feels intuitive to everyone. The advantage of dates formatted like 2017-07-17 is that they follow the order of largest to smallest units: year, month, and day. This format also doesn't overlap in ambiguous ways with other date formats, unlike some regional formats that switch the position of month and day numbers. These reasons, and the fact this date format is an ISO standard, are why it is the recommended date format for changelog entries.

#### Inconsistent Changes

A changelog which only mentions some of the changes can be as dangerous as not having a changelog. While many of the changes may not be relevant - for instance, removing a single whitespace may not need to be recorded in all instances - any important changes should be mentioned in the changelog. By inconsistently applying changes, your users may mistakenly think that the changelog is the single source of truth. It ought to be. With great power comes great responsibility - having a good changelog means having a consistently updated changelog.

- 1: https://www.gnu.org/prep/standards/html_node/Style-of-Change-Logs.html#Style-of-Change-Logs "GNU Coding Standards: Style of Change Logs"
- 2: https://keepachangelog.com/en/1.1.0/ "Keep a Changelog"
- 3: https://semver.org/ "Semantic Versioning 2.0.0"
- 4: https://en.wikipedia.org/wiki/ISO_8601 "ISO 8601"
<!--- 5: https://chris.beams.io/posts/git-commit/ "How to Write a Git Commit Message"-->
