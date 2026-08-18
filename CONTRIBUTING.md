# Contributing to miri-standard

Thank you for your interest in contributing to the miri-standard project! This document provides guidelines and
information about how to contribute.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE-OF-CONDUCT.md). By
participating, you are expected to uphold this code.

## Pre-commit Hook

The repository ships its CI checks as a pre-commit hook. Enable it once per clone:

```bash
git config core.hooksPath .githooks
```

It runs markdownlint, cspell, relative-link verification, checklist-weight and check-definition coherence, and a
404 check on external links added by the commit. Full external-link checking runs in CI only.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your contribution
4. Make your changes
5. Test your changes
6. Submit a pull request

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Before creating an issue, please search existing issues to avoid duplicates
- Provide as much detail as possible, including:
  - Clear description of the issue
  - Steps to reproduce (for bugs)
  - Expected vs actual behavior
  - Environment details

### Suggesting Enhancements

- Use GitHub issues to suggest new features or improvements
- Provide a clear description of the enhancement
- Explain why this enhancement would be useful
- Consider providing examples or mockups if applicable

### Contributing Code

- Follow the existing code style and conventions
- Write clear, concise commit messages
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass before submitting

## Development Process

### Standards Development

This project follows a standards development process:

1. **Proposal Phase**: New standards or changes are proposed via GitHub issues or discussions
2. **Draft Phase**: Proposals are developed into draft specifications
3. **Review Phase**: Community review and feedback
4. **Approval Phase**: Final review and approval by maintainers
5. **Publication Phase**: Standards are published and versioned

### Branch Strategy

- `main`: Stable, released standards
- `develop`: Integration branch for new features
- Feature branches: `feature/description` for new work
- Release branches: `release/version` for preparing releases

## Submitting Changes

### Pull Request Process

1. Ensure your branch is up to date with the main branch
2. Create a pull request with:
   - Clear title and description
   - Reference to related issues
   - List of changes made
   - Any breaking changes noted
3. Ensure all checks pass
4. Request review from maintainers
5. Address any feedback
6. Maintain the pull request until merged

### Commit Guidelines

- Use clear, descriptive commit messages
- Follow conventional commit format when possible:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation changes
  - `refactor:` for code refactoring
  - `test:` for test changes

### Documentation

- Update relevant documentation for any changes
- Include inline code comments where appropriate
- Update README.md if the change affects usage
- Add or update examples as needed

## Review Process

All contributions go through a review process:

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Peer Review**: Other contributors review the code
3. **Maintainer Review**: Project maintainers provide final approval
4. **Merge**: Changes are merged into the appropriate branch

## Community

### Communication Channels

- GitHub Discussions: For general questions and discussions
- GitHub Issues: For bug reports and feature requests
- [Add other communication channels as they become available]

### Meetings

- [Information about regular community meetings will be added here]

### Special Interest Groups (SIGs)

- [Information about SIGs will be added as they are formed]

## Recognition

Contributors are recognized in several ways:

- Listed in the project's contributors
- Mentioned in release notes for significant contributions
- Invited to join the project as maintainers for sustained contributions

## Getting Help

If you need help with contributing:

1. Check existing documentation
2. Search through GitHub issues and discussions
3. Create a new issue with the "question" label
4. Reach out to maintainers

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the
project (MIT License).

## Developer Certificate of Origin (DCO)

This project requires all contributors to sign off on their commits, indicating that they have the right to submit the
code under the project's license. See [DCO](DCO) for more details.

To sign off on a commit, add the `-s` flag to your git commit command:

```bash
git commit -s -m "Your commit message"
```

Thank you for contributing to miri-standard!
