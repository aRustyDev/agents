## Frequently Asked Questions

### Is there a standard changelog format?

Not really. There's the GNU changelog style guide, or the two-paragraph-long GNU NEWS file "guideline". Both are inadequate or insufficient.

This project aims to be a better changelog convention. It comes from observing good practices in the open source community and gathering them.

Healthy criticism, discussion and suggestions for improvements are welcome.

### What should the changelog file be named?

Call it CHANGELOG.md. Some projects use HISTORY, NEWS or RELEASES.

While it's easy to think that the name of your changelog file doesn't matter that much, why make it harder for your end users to consistently find notable changes?

### What about GitHub Releases?

It's a great initiative. Releases can be used to turn simple git tags (for example a tag named v1.0.0) into rich release notes by manually adding release notes or it can pull annotated git tag messages and turn them into notes.

GitHub Releases create a non-portable changelog that can only be displayed to users within the context of GitHub. It's possible to make them look very much like the Keep a Changelog format, but it tends to be a bit more involved.

The current version of GitHub releases is also arguably not very discoverable by end-users, unlike the typical uppercase files (README, CONTRIBUTING, etc.). Another minor issue is that the interface doesn't currently offer links to commit logs between each release.

### Can changelogs be automatically parsed?

It’s difficult, because people follow wildly different formats and file names.

Vandamme is a Ruby gem created by the Gemnasium team and which parses many (but not all) open source project changelogs.

### What about yanked releases?

Yanked releases are versions that had to be pulled because of a serious bug or security issue. Often these versions don't even appear in change logs. They should. This is how you should display them:

`## [0.0.5] - 2014-12-13 [YANKED]`

The [YANKED] tag is loud for a reason. It's important for people to notice it. Since it's surrounded by brackets it's also easier to parse programmatically.

### Should you ever rewrite a changelog?

Sure. There are always good reasons to improve a changelog. I regularly open pull requests to add missing releases to open source projects with unmaintained changelogs.

It's also possible you may discover that you forgot to address a breaking change in the notes for a version. It's obviously important for you to update your changelog in this case.

### How can I contribute?

This document is not the truth; it’s my carefully considered opinion, along with information and examples I gathered.

This is because I want our community to reach a consensus. I believe the discussion is as important as the end result.

So please pitch in.
Conversations

I went on The Changelog podcast to talk about why maintainers and contributors should care about changelogs, and also about the motivations behind this project.

- 1: https://www.gnu.org/prep/standards/html_node/Style-of-Change-Logs.html#Style-of-Change-Logs "GNU Coding Standards: Style of Change Logs"
- 2: https://keepachangelog.com/en/1.1.0/ "Keep a Changelog"
- 3: https://semver.org/ "Semantic Versioning 2.0.0"
- 4: https://en.wikipedia.org/wiki/ISO_8601 "ISO 8601"
<!--- 5: https://chris.beams.io/posts/git-commit/ "How to Write a Git Commit Message"-->
