
[fork]: https://github.com/sadanaragoor/CSC510Group17_Proj3/fork
[pr]: https://github.com/sadanaragoor/CSC510Group17_Proj3/compare
[code-of-conduct]: CODE_OF_CONDUCT.md
[install-guide]: INSTALL.md
[pep8]: https://peps.python.org/pep-0008/

# 🍔 Contributing to StackShack v2.0

Hi there! We're thrilled that you'd like to contribute to this project. Your help is essential for keeping it great.

**StackShack v2.0** features gamification, payment systems, dietary preferences, inventory management, staff scheduling, and surprise box functionality - all with 75%+ test coverage and 493 automated tests!

Please note that this project is released with a [Contributor Code of Conduct][code-of-conduct]. By participating in this project you agree to abide by its terms.

## Issues and PRs

If you have suggestions for how this project could be improved, or want to report a bug, [open an issue](https://github.com/sadanaragoor/CSC510Group17_Proj3/issues)! We'd love all and any contributions.

We'd also love PRs. If you're thinking of a large pull request (PR), we advise opening up an issue first to talk about it, though!

## Submitting a Pull Request

1.  **[Fork][fork] and clone the repository.**
2.  **Follow the [Installation Guide][install-guide]** to set up your virtual environment, install dependencies, and configure your local database (SQLite or MySQL).
3.  **Make sure all 493 tests pass on your machine.** From the `proj2/stackshack/` directory, run:
    ```bash
    pytest
    ```
    Or with coverage:
    ```bash
    pytest --cov=models --cov=controllers --cov=routes --cov=services
    ```
4.  **Run code quality checks:**
    ```bash
    # Format with Black
    black .
    
    # Lint with Ruff
    ruff check .
    ```
5.  **Create a new branch:** `git checkout -b my-branch-name`.
6.  **Make your change, add tests,** and make sure the tests still pass with your changes (maintain 75%+ coverage).
7.  **Push to your fork** and [submit a pull request][pr].
8.  Pat yourself on the back and wait for your pull request to be reviewed and merged!

Here are a few things you can do that will increase the likelihood of your pull request being accepted:

* **Follow Python style conventions.** We follow [PEP 8][pep8] and use Black formatter (line-length: 88).
* **Write and update tests.** We have a comprehensive test suite with 493 tests (117 unit + 376 integration). Any new features must be accompanied by new tests with 75%+ coverage.
* **Run linters.** Use Black for formatting and Ruff for linting before submitting.
* **Keep your changes focused.** If there are multiple changes you would like to make that are not dependent upon each other, please submit them as separate pull requests.
* **Write good commit messages.** Use conventional commit format when possible.
* **Update documentation.** Update README.md and other docs if you add new features.

Work-in-progress pull requests are also welcome to get feedback early on, or if you are blocked on something.

## Code Quality Standards

We maintain high code quality standards:
- ✅ 75%+ test coverage
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Bandit security scanning
- ✅ All tests passing in CI/CD

## Resources

* [How to Contribute to Open Source](https://opensource.guide/how-to-contribute/)
* [Using Pull Requests](https://help.github.com/articles/about-pull-requests/)
* [GitHub Help](https://help.github.com)
