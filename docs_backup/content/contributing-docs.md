# Contributing to Documentation

Help us keep ReViewPoint’s documentation clear, accurate, and professional! Here’s how you can contribute:

## First-Time Contributor Checklist

- [ ] Read the [Development Guidelines](dev-guidelines.md) and this page.
- [ ] Fork the repository and clone it locally.
- [ ] Create a new branch for your changes.
- [ ] Use the provided templates for new docs (see below).
- [ ] Run Prettier and markdownlint on your changes.
- [ ] Preview your changes locally with `hatch run mkdocs serve` (see [How to Use the Docs](how-to-use-docs.md)).
- [ ] Ensure all links and cross-references work.
- [ ] Open a pull request with a clear description.
- [ ] Respond to review comments and update as needed.

## How to Propose a Docs Change

1. Open an issue or discussion if your change is significant (e.g., new section, major rewrite).
2. For small fixes (typos, formatting), open a PR directly.
3. Use clear commit messages and PR titles (see [Developer Guidelines](dev-guidelines.md)).
4. Link to the relevant issue/ticket if applicable.

## Example PRs

- [Example: Add new backend module docs](https://github.com/filip-herceg/ReViewPoint/pull/1)
- [Example: Fix typos in setup guide](https://github.com/filip-herceg/ReViewPoint/pull/2)

## Best Practices

- Follow the layered, directory-first structure for all new docs.
- Use the provided templates for file-level documentation.
- Cross-reference related files, tests, and modules.
- Fix Markdown lint errors before submitting changes.
- Use clear, concise language and professional formatting.

## Style Guide

- Headings: Use `#` for titles, `##` for sections, and so on.
- Lists: Add blank lines before and after lists.
- Code: Use fenced code blocks with language hints (e.g., `python`, `js`).
- Admonitions: Use `!!! note`, `!!! warning`, etc. for callouts.
- Diagrams: Use ASCII or Mermaid for architecture diagrams.

## Templates

- See the `COMPONENT_TEMPLATE.md`, `PAGE_TEMPLATE.md`, etc. in the frontend docs for examples.
- Backend templates are in the corresponding backend docs folders.

## Submitting Changes

- Open a pull request with a clear description of your changes.
- Ensure all links and cross-references work.
- Run Markdown linting before submitting.

---

_Thank you for helping make ReViewPoint’s docs world-class!_
