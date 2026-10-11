## Code Style
When modifying existing code, match the patterns already in the file.
If the file uses callbacks, don't switch to async/await.
If the file uses class components, don't refactor to hooks.
Match the existing style, even if you'd do it differently.
## Abstractions
Do not create abstractions unless they reduce real, measurable complexity.
No interfaces with a single implementation.
No factory functions that produce one type.
No wrapper classes that just delegate to another class.
Three similar lines of code is better than a premature abstraction.
## Tests
Never modify existing tests unless the change intentionally updates the behavior they cover.
If a test fails after your change, that means YOUR change is wrong, not the test.
Fix your code to make the existing test pass.
## Comments
Default to writing no comments.
Only add a comment when the WHY is non-obvious.
Never comment WHAT the code does.
Never reference the current task, ticket, or fix in a comment.
## Scope
Keep changes scoped to exactly what was requested.
Don't "improve" adjacent code.
Don't refactor things that aren't broken.
Don't add features that weren't asked for.
## Error Handling
Don't add error handling for scenarios that can't happen.
Trust internal function contracts.
Only validate at system boundaries: user input, API responses, file reads.
## Stack
- Runtime: Node.js 20
- Framework: Next.js 14 (App Router)
- Database: PostgreSQL with Prisma
- Styling: Tailwind CSS
- Testing: Vitest + Playwright
- Package manager: pnpm
## Project Structure
- `src/app/` - Next.js App Router pages and layouts
- `src/components/` - Reusable UI components
- `src/lib/` - Business logic and utilities
- `src/server/` - Server-only code
- `prisma/` - Database schema and migrations
- `tests/` - Test files mirror src/ structure
## Naming Conventions
- Files: kebab-case (user-profile.ts)
- Components: PascalCase (UserProfile.tsx)
- Functions: camelCase
- Database tables: snake_case
- Environment variables: SCREAMING_SNAKE_CASE
- Test files: [name].test.ts alongside source
## Imports
Use path aliases: `@/components`, `@/lib`, `@/server`
Never use relative imports that go up more than one level.
Prefer named exports over default exports.
## Database
All database queries go through Prisma.
Never write raw SQL unless Prisma can't express the query.
All queries go in `src/server/db/`.
Use transactions for multi-table operations.
## Testing
Write tests for business logic and API endpoints.
Test behavior, not implementation details.
Don't mock what you don't own.
Use factory functions from `tests/factories/` for test data.
Run `pnpm test` before claiming any task is done.
## Verification
After making changes, run these before reporting done:
- `pnpm test`
- `pnpm lint`
- `pnpm typecheck`
If any fail, fix the issue first.
## Security
Never commit .env files, API keys, tokens, or credentials.
Never log sensitive data.
Never put secrets in comments or test fixtures.
## Git
Use conventional commit format: type(scope): description
Types: feat, fix, refactor, test, docs, chore
Keep commits focused on one change.
Don't mention AI or "generated" in commit messages.
## Dependencies
Don't add new dependencies for something a few lines of code can handle.
Don't add new dependencies when existing ones cover the use case.
## Communication
When done, explain what you changed and why in 2-3 sentences.
If you found something unexpected, mention it.
If you made a judgment call, explain your reasoning.