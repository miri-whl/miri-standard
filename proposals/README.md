# Proposals

This directory contains proposals for new specifications, significant changes to existing specifications, and other
major project initiatives.

## Overview

The proposal process allows community members to suggest new standards, modifications to existing standards, or other
significant changes to the project. All proposals go through a structured review process before being accepted for
development.

## Proposal Process

### 1. Initial Discussion

Before creating a formal proposal:

- Discuss the idea in GitHub Discussions
- Get feedback from the community
- Ensure the proposal aligns with project goals
- Check if similar work already exists

### 2. Proposal Creation

Create a new proposal by:

1. Copying the [proposal template](template.md)
2. Creating a new file: `YYYYMMDD-proposal-title.md`
3. Filling out all sections of the template
4. Submitting a pull request

### 3. Review Process

1. **Initial Review**: SIG-Spec reviews for completeness and alignment
2. **Community Review**: 2-week community review period
3. **Revision**: Address feedback and update proposal
4. **Decision**: SIG-Spec and maintainers make final decision

### 4. Implementation

Accepted proposals move to implementation:

- Draft specification created in [standards/](../standards/)
- Implementation work begins
- Regular progress updates provided

## Proposal Status

### Active Proposals

- [Consumption Specification (RFC)](20260821-consumption-specification.md) — **Draft**, deferred to post-v0.2. A
  consumer-side spec closing the producer→consumer loop (task-to-document map, discovery contract, consumer conformance
  profile, verification recipe, paired fixture). Panel pre-reviewed 2026-08-21: endorse-with-changes.

### Accepted Proposals

*(Accepted proposals will be listed here).*

### Rejected Proposals

*(Rejected proposals are archived for reference).*

## Proposal Template

Use the [proposal template](template.md) for all new proposals. The template includes:

- **Metadata**: Title, authors, status, dates
- **Abstract**: Brief summary of the proposal
- **Motivation**: Why this proposal is needed
- **Specification**: Detailed technical specification
- **Implementation**: Implementation considerations
- **Security**: Security implications
- **Alternatives**: Alternative approaches considered
- **References**: Related work and standards

## Guidelines

### Good Proposals

- **Clear Problem Statement**: Clearly define the problem being solved
- **Detailed Solution**: Provide sufficient technical detail
- **Implementation Plan**: Show how the proposal will be implemented
- **Community Benefit**: Demonstrate value to the community
- **Compatibility**: Consider impact on existing standards

### Review Criteria

Proposals are evaluated on:

- **Technical Merit**: Is the solution technically sound?
- **Community Need**: Does this address a real community need?
- **Feasibility**: Can this be realistically implemented?
- **Compatibility**: Does this maintain backward compatibility?
- **Scope**: Is the scope appropriate for the project?

## Contributing

To contribute a proposal:

1. Review existing proposals and discussions
2. Follow the proposal process outlined above
3. Engage with community feedback constructively
4. Be prepared to champion your proposal through implementation

## Resources

- [Proposal Template](template.md)
- [SIG-Spec](../community/sig-spec/): Specification development group
- [Standards](../standards/): Current specifications
- [Contributing Guidelines](../CONTRIBUTING.md)

## Contact

- **Proposal Questions**: Use GitHub Discussions with the `proposal` label
- **Process Questions**: Contact SIG-Spec leads
- **Submit Proposals**: Create pull request with new proposal file
