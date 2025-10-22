# Contributing

## Branching
- `main` is stable.
- Feature branches: `feat/<short>`, fixes: `fix/<short>`.

## Conventional Commits
Examples:
- `feat(jobs): add salary filter`
- `fix(auth): correct token expiry`
- `docs: update README quickstart`

## Dev flow
1. `scripts/bootstrap.sh` (once) then `scripts/dev.sh`
2. Add tests for your change: `scripts/test.sh`
3. Run quality gate: `scripts/verify.sh`
4. Open PR using the template.
