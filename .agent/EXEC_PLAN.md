# ResumeAI Execution Plan

## Product objective and user problem

Make ResumeAI a coherent, trustworthy local workspace where a job seeker can turn a complete career history into truthful, targeted application materials and keep the resulting applications organized. The product must explain what is local, what requires an AI provider, what data is saved, and what the user should do next.

## Current state

The repository contains a FastAPI/SQLite backend, a React/Vite interface, Docker deployment files, and backend API tests. Several useful capabilities were newer than the README. This run established and repaired the build, test, runtime, responsive, accessibility, persistence, and primary end-to-end behavior.

## Desired state

- A new user can understand the workflow and recover from having no profile or no data.
- The core create/import profile -> assess job -> generate/edit/export -> track flow is clear and works.
- Provider-free behavior is honest and useful; provider failures are actionable.
- Backend and frontend have repeatable, passing quality gates.
- Local and Docker setup, privacy model, limitations, and deployment requirements are accurately documented.

## Scope and non-goals

In scope: the current repository only; product clarity, critical workflows, validation, accessibility, responsive behavior, error/loading/empty/success states, focused tests, operational setup, and documentation.

Non-goals: multi-user authentication, production deployment, remote publishing, destructive database migrations, broad framework replacement, fabricated product claims, or a complete hosted SaaS security model.

## Architecture summary

The Vite React single-page app calls REST endpoints under `/api`. FastAPI routers coordinate deterministic parsers/scorers, optional OpenAI or Anthropic generation services, SQLAlchemy models, SQLite persistence, and DOCX export. Nginx serves the production frontend and proxies API traffic in Docker.

## Milestones and acceptance criteria

### 1. Stabilize and baseline

- [x] Install dependencies only where absent.
- [x] Run backend tests and bytecode compilation.
- [x] Run frontend build and any existing checks.
- [x] Start both services and exercise health and main routes.
- [x] Record pre-existing failures verbatim enough to reproduce.

Validation: `python -m pytest backend/tests -q`; `python -m compileall -q backend`; `npm --prefix frontend run build`; local health checks.

### 2. Product clarity and primary journey

- [x] Make onboarding and next actions unambiguous.
- [x] Remove or repair misleading, dead, or unsafe interactions.
- [x] Ensure profile-empty, no-result, provider-error, and success feedback are useful.
- [x] Keep all generated claims grounded in saved user data.

Validation: focused tests, production build, manual primary-journey walk-through.

### 3. Interface and design quality

- [x] Establish coherent tokens, typography, spacing, and shared states.
- [x] Verify navigation, forms, focus, labels, feedback, mobile layout, and reduced motion.
- [x] Inspect representative desktop and mobile screens in the running product.

Validation: frontend checks/build and real browser inspection at desktop/mobile widths.

### 4. Engineering quality and safety

- [x] Add missing high-value checks and focused tests.
- [x] Strengthen validation and safe error propagation.
- [x] Review CORS, uploads, database ownership boundaries, logs, secrets, and container persistence.
- [x] Ensure CI or a single documented validation path covers the repository.

Validation: all automated checks, API negative cases, configuration inspection.

### 5. Documentation and operations

- [x] Reconcile README features, architecture, setup, environment variables, commands, deployment, privacy, limitations, troubleshooting, and roadmap.
- [x] Keep environment examples safe and complete.
- [x] Validate container configuration where tooling permits.

### 6. Final review and second pass

- [x] Re-run the full product and validations.
- [x] Critique the three weakest remaining areas.
- [x] Implement the highest-value safe improvement after the first working result.
- [x] Review the final diff for regressions, secrets, debug artifacts, and unfinished work.
- [x] Update final status and recovery instructions.

## Decisions and reasoning

- Treat this as a local-first, single-user product because resource ownership is expressed through caller-supplied user IDs and no authentication exists. Documentation and UI must not imply production multi-user isolation.
- Preserve the current React/FastAPI architecture; it already supports the intended workflow and has meaningful backend coverage.
- Use deterministic functionality as the no-key baseline and make provider requirements explicit at the moment they matter.

## Discoveries

- The README roadmap lists cover letters and job tracking although those features are already implemented.
- The frontend initially lacked lint and test scripts; the completed `check` command now runs ESLint, Vitest, and a production build.
- The repository started clean on `claude/implement-claude-md-3rdCG` at commit `b67127b`.
- Initial backend tests could not collect because `EmailStr` required an undeclared package.
- Initial mobile inspection showed 507 px of document width in a 390 px viewport.
- Saved results omitted the original job description and retained only a numeric score.
- The Docker database file was outside its declared persistent volume.

## Known issues

- The app remains deliberately single-user and unauthenticated; resource IDs are not production authorization boundaries.
- Provider-backed generation was not called without user-supplied credentials.
- Scanned PDF import still requires external OCR.

## Recovery instructions

The productization run is complete. For future work, inspect `git status`, this plan, and `PRODUCTIZATION_STATUS.md`; then run the validation commands documented in the README. Preserve any user changes made after this plan was written. The isolated Docker validation project and its empty test volume were removed after validation; no user data was touched.

## Final results

All milestones passed. The app now has a documented local-first product contract, a repaired primary workflow, responsive and accessible navigation/forms/states, durable saved-result context, strengthened API ownership and validation rules, repeatable frontend/backend/CI checks, and a production-like Docker path with verified persistence and security configuration. Final automated checks passed with 62 backend tests and 3 frontend tests; desktop, mobile, dark-theme, and containerized runtime behavior were inspected manually. The remaining limitations are intentional follow-on scope: authentication for multi-user deployment, live provider testing with user-supplied credentials, and OCR for scanned PDFs.
