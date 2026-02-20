AGENTS.md

Purpose
- This guide helps agentic coding agents operate in this repository. It documents
  build/lint/test commands, plus code style guidelines and repository-specific
  conventions (imports, formatting, types, naming, error handling, etc.).
- It also notes Cursor rules and Copilot guidance if present in the repo.

Scope
- Language-agnostic guidance with concrete examples for common ecosystems.
- When a project uses a specific toolchain, prefer the project scripts in
  package.json, pyproject.toml/requirements, go.mod, pom.xml, or build.gradle
  to determine the exact commands. Use the examples as templates.

Quick Start
- Detect toolchain by looking for standard files: package.json, pyproject.toml,
  go.mod, pom.xml, build.gradle, Makefile, etc.
- Prefer running the project-defined scripts (e.g., npm run build, pytest, go test).
- For single-test execution, use framework-specific selectors described below.

Build/Lint/Test Commands
- Node.js / JavaScript / TypeScript (if package.json exists)
  - Build: npm run build | yarn build | pnpm build
  - Lint:  npm run lint  | yarn lint  | pnpm lint
  - Lint autofix (if configured): npm run lint:fix | yarn lint --fix | pnpm lint
  - Tests:  npm test | yarn test | pnpm test
  - Single test (example patterns):
    - Jest: npm test -- -t "should render Home" 
      or npx jest -t "should render Home"
    - Vitest: npm test -t "should render Home" 
      (some projects proxy to Vitest via Jest CLI)
    - Mocha: mocha -grep "should render Home" -R spec
  - Subset/tests by path: npm test -- tests/home.test.js

- Python (if pyproject.toml/requirements.txt or setup.py exists)
  - Test: pytest
  - Single test: pytest -k "test_name" -q
  - Lint: flake8 | ruff check .
  - Type checks: mypy .

- Go (if go.mod exists)
  - Test: go test ./...
  - Single test: go test -run TestName ./...
  - Lint: golangci-lint run

- Rust (if Cargo.toml exists)
  - Test: cargo test
  - Single test: cargo test tests::my_test
  - Lint: cargo fmt -- --check; cargo clippy -- -D warnings

- Java / Kotlin (if pom.xml or build.gradle exists)
  - Maven (tests): mvn -Dtest=MyTest test
  - Gradle (tests): ./gradlew test --tests com.example.MyTest

- Other tips
  - If you are unsure about the language, start with a quick static check
    (lint/type-check) before running tests.
  - Run tests with verbose output when debugging flaky tests (e.g., -Dtest=Pattern).

Code Style Guidelines
- General
  - Follow the project’s lint and formatter configuration (eslint/tslint, flake8/ruff, gofmt, rustfmt, etc.).
  - Code should be readable, well-documented, and have deterministic behavior in tests.

- Imports / Dependencies
  - Group imports in the following order: standard library, third-party, project/internal.
  - Alphabetize within groups; avoid unused dependencies and circular imports.
  - Prefer dependency injection to reduce tight coupling.
  - Use path aliases consistently where supported (e.g., @src/ or similar).

- Formatting
  - Respect the project formatter (Prettier, Black, gofmt, rustfmt, etc.).
  - Use 2-space indentation for most languages; adjust to project defaults.
  - End files with a newline; avoid trailing whitespace.
  - Prefer explicit line breaks for long expressions; keep line length reasonable (100–120 chars).

- Types & API Shapes
  - Enable strict type checking where available (TypeScript: "strict": true; Python: type hints; Go: static types).
  - Prefer explicit types over inference when it improves readability.
  - Avoid using any/unknown loosely; prefer precise types; use type aliases for complex shapes.
  - Use readonly or immutability where appropriate.

- Naming Conventions
  - Functions/methods: camelCase; variables: camelCase; classes/types: PascalCase.
  - Constants: UPPER_SNAKE_CASE; enums: PascalCase.
  - Async function names: end with Async when the convention demands it.

- Error Handling
  - Do not swallow errors; attach context and preserve stack traces.
  - Define domain-specific error classes (e.g., ValidationError, NotFoundError).
  - Fail fast on invalid inputs; validate early and clearly.
  - Do not log sensitive data; use a centralized logger instead of console logs in libraries.

- Testing
  - Tests should be deterministic, fast, and isolated from IO where possible.
  - Mock external dependencies; provide fixtures that are small and clear.
  - Cover both success and error paths; include edge-case tests.

- Documentation
  - Public APIs must be documented with JSDoc/TSDoc, Python docstrings, or language equivalents.
  - Complex logic should include concise comments explaining intent; avoid obvious comments.

- Cursor Rules
- If Cursor rules exist, they live in .cursor/rules/ or .cursorrules. Port or reference
  them here for agent compliance and CI expectations.

- Copilot Rules
- If Copilot guidelines exist (in .github/copilot-instructions.md), summarize key
  constraints for agents and reviewers.

- Environment & CI
- Run lint, type checks, and tests in CI; fail fast on errors.
- Do not commit secrets; use environment variables for credentials.
- Document how to reproduce failures locally, including required env vars.

- Contributing this guide
- If you modify rules, update AGENTS.md and include a brief rationale for changes.
- List any script paths or config references for quick lookup.

Appendix: How to use this guide
- Start with a quick static check (lint/type-check).
- Apply small, well-scoped edits with clear commit messages.
- Validate locally before escalation to CI.
