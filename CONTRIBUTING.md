# Contributing to RC and RL Calculator

Thanks for your interest in contributing!

## Coding Standards
- Follow [PEP 8](https://peps.python.org/pep-0008/) for style.
- Use type hints where practical and include docstrings for public functions.
- Keep functions focused and cover new code with tests.

## Testing
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the test suite before submitting a pull request:
   ```bash
   PYTHONPATH=. pytest
   ```

## Pull Request Workflow
1. Fork the repository and create a feature branch from `main`.
2. Make your changes and commit with clear, descriptive messages.
3. Ensure `PYTHONPATH=. pytest` passes.
4. Open a pull request describing the changes and link any relevant issues.

By contributing, you agree to abide by the project's [Code of Conduct](CODE_OF_CONDUCT.md).
