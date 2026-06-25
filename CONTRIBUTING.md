# Contributing to Transaction Ranking System

Thank you for your interest in contributing! This document provides guidelines and instructions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/transaction-ranking-system.git`
3. Add upstream remote: `git remote add upstream https://github.com/original/transaction-ranking-system.git`
4. Create feature branch: `git checkout -b feature/your-feature-name`

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database config
python -c "from app.db.database import init_db; init_db()"
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Code Style

### Python

- Follow PEP 8
- Use type hints for all functions
- Max line length: 100 characters
- Format with Black: `black app/`
- Lint with Pylint: `pylint app/`

### JavaScript/React

- Use ESLint: `npm run lint`
- Use Prettier for formatting
- Functional components preferred
- Use hooks for state management

## Commit Messages

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Test additions/updates
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Build, deps, etc.

Examples:
```
feat(ranking): add consistency score calculation
fix(transaction): prevent race condition in updates
docs(api): add endpoint documentation
test(services): add transaction service tests
```

## Pull Request Process

1. Update README if adding features
2. Add tests for new functionality
3. Ensure all tests pass: `pytest`
4. Update docstrings and comments
5. Keep commits clean and logical
6. Write descriptive PR description

## Testing

```bash
cd backend

# Run all tests
pytest

# With coverage
pytest --cov=app

# Specific test
pytest tests/test_transactions.py::test_create_transaction_success

# Watch mode
pytest-watch
```

Target coverage: 80%+

## Database Changes

Use Alembic for migrations:

```bash
# Create migration
alembic revision --autogenerate -m "add_new_column"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Documentation

- Docstrings: Google style format
- Comments: Explain "why", not "what"
- README: Update with feature changes
- API Docs: Use proper OpenAPI format

## Code Review

- Be respectful and constructive
- Ask questions instead of making demands
- Suggest improvements, don't criticize
- Approve once satisfied with changes

## Issues

Before starting work:
1. Check if issue exists
2. Comment on issue to claim it
3. Reference issue in PR: "Fixes #123"

## Performance

- Profile code before optimizing
- Use indexing for frequent queries
- Cache expensive operations
- Monitor database query performance

## Security

- Never commit secrets or .env files
- Use parameterized queries
- Validate all inputs
- Use HTTPS in production
- Keep dependencies updated

## Questions?

- Open discussion on GitHub
- Check existing documentation
- Ask in issues or PR comments

## License

By contributing, you agree your code will be licensed under MIT License.

---

Happy coding! 🚀
