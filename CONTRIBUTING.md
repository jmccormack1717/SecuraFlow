# Contributing to SecuraFlow

Thank you for your interest in contributing to SecuraFlow! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker)
- Git

### Getting Started

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SecuraFLow.git
   cd SecuraFLow
   ```

2. **Set up the backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your database URL
   python ml/train.py
   ```

3. **Set up the frontend:**
   ```bash
   cd ../frontend
   npm install
   cp .env.example .env
   # Edit .env with your API URL
   ```

4. **Initialize the database:**
   ```bash
   cd ../backend
   python init_db.py
   ```

## Development Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

3. **Run tests:**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v --cov=app
   
   # Frontend tests
   cd ../frontend
   npm run test
   npm run lint
   ```

4. **Commit your changes:**
   ```bash
   git commit -m "feat: add your feature description"
   ```
   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `style:` for formatting changes

5. **Push and create a Pull Request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

### Python (Backend)

- Follow **PEP 8** style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use meaningful variable and function names
- Add docstrings for functions and classes

### TypeScript/React (Frontend)

- Follow ESLint rules (configured in the project)
- Use functional components with hooks
- Use TypeScript types/interfaces
- Follow React best practices
- Use meaningful component and variable names

## Testing

### Backend Testing

- Write tests for new features and bug fixes
- Aim for high test coverage
- Use pytest fixtures for common setup
- Test both success and error cases

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Frontend Testing

- Write unit tests for components
- Test user interactions
- Use React Testing Library

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:coverage
```

## Pull Request Guidelines

1. **Keep PRs focused:** One feature or bug fix per PR
2. **Write clear descriptions:** Explain what and why
3. **Link issues:** Reference related issues
4. **Update documentation:** Update README/docs if needed
5. **Ensure tests pass:** All CI checks must pass
6. **Request review:** Tag relevant maintainers

## Reporting Bugs

When reporting bugs, please include:

- **Description:** Clear description of the bug
- **Steps to reproduce:** Detailed steps to reproduce
- **Expected behavior:** What should happen
- **Actual behavior:** What actually happens
- **Environment:** OS, Python/Node versions, etc.
- **Screenshots/logs:** If applicable

## Feature Requests

For feature requests:

- **Use case:** Why is this feature needed?
- **Proposed solution:** How should it work?
- **Alternatives:** Other solutions considered

## Questions?

Feel free to open an issue for questions or discussions. We're happy to help!

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing to SecuraFlow! 🚀

