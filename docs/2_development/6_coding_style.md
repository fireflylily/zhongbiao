# Coding Style Guide

This document outlines the coding style and conventions to be followed when contributing to the AI-Tender-System project.

## Python (Backend)

-   **Style Guide**: Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
-   **Code Formatting**: Use `black` with a line length of 120 characters.
-   **Type Hinting**: Use Python 3.11+ type hints for all function signatures and variable declarations.
-   **Docstrings**: Use Google-style docstrings for all modules, classes, and functions.
-   **Imports**: Sort imports using `isort`.

## JavaScript/TypeScript (Frontend)

-   **Style Guide**: Follow the [Vue.js Style Guide](https://vuejs.org/v2/style-guide/).
-   **Code Formatting**: Use `prettier`.
-   **Naming Conventions**:
    -   Components: `PascalCase`
    -   Files: `kebab-case`
    -   Variables/Functions: `camelCase`
    -   Constants: `UPPER_SNAKE_CASE`

## Git Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Format:**

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

**Types:**

-   `feat`: A new feature
-   `fix`: A bug fix
-   `docs`: Documentation only changes
-   `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc)
-   `refactor`: A code change that neither fixes a bug nor adds a feature
-   `test`: Adding missing tests or correcting existing tests
-   `chore`: Changes to the build process or auxiliary tools and libraries

**Example:**

```
feat(api): add endpoint for project creation

Adds the `POST /api/projects` endpoint to allow for the creation of new tender projects.

Closes #123
```
