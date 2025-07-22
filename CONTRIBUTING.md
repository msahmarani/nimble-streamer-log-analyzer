# Contributing to Nimble Streamer Log Analyzer

Thank you for your interest in contributing to the Nimble Streamer Log Analyzer! This document provides guidelines for contributing to the project.

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- **Search existing issues** first to avoid duplicates
- **Use issue templates** when available
- **Provide detailed information** including:
  - Operating system and Python version
  - Steps to reproduce the bug
  - Expected vs actual behavior
  - Log files or error messages (sanitized)
  - Screenshots if applicable

### ✨ Feature Requests
- **Check existing issues** for similar requests
- **Describe the use case** clearly
- **Explain the benefit** to users
- **Consider implementation complexity**
- **Provide mockups** or examples if helpful

### 📝 Documentation
- **Fix typos** and improve clarity
- **Add examples** and use cases
- **Improve installation instructions**
- **Update outdated information**
- **Translate documentation** (future consideration)

### 💻 Code Contributions
- **Bug fixes**
- **New features**
- **Performance improvements**
- **Code refactoring**
- **Test coverage improvements**

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Git for version control
- Basic understanding of Python, pandas, and Dash
- Familiarity with log analysis concepts

### Development Setup

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/nimble-streamer-log-analyzer.git
   cd nimble-streamer-log-analyzer
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Start web GUI
   python web_gui.py
   
   # Or use launcher
   start_web_gui.bat  # Windows
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 🔧 Development Workflow

### Branch Strategy
- **main** - Production-ready code
- **develop** - Integration branch for new features
- **feature/feature-name** - Individual feature branches
- **bugfix/bug-description** - Bug fix branches
- **hotfix/critical-fix** - Critical production fixes

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow coding standards (see below)
   - Add/update tests if applicable
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run the application
   python web_gui.py
   
   # Test with sample log files
   # Verify all tabs work correctly
   # Check error handling
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add new feature description"
   ```

5. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## 📋 Coding Standards

### Python Code Style
- **Follow PEP 8** style guidelines
- **Use meaningful variable names**
- **Add docstrings** to functions and classes
- **Handle exceptions** appropriately
- **Keep functions focused** and modular

### Code Organization
```
nimble-streamer-log-analyzer/
├── web_gui.py              # Main web interface
├── json_log_analyzer.py    # Multi-format analyzer  
├── nimble_app_log_parser.py # Nimble app log parser
├── log_analyzer.py         # Traditional log analyzer
├── tests/                  # Test files (future)
├── docs/                   # Documentation (future)
└── examples/               # Example files (future)
```

### Commit Message Format
Use conventional commits format:
```
type(scope): description

feat: add new feature
fix: fix bug description  
docs: update documentation
style: formatting changes
refactor: code refactoring
test: add tests
chore: maintenance tasks
```

### Documentation Standards
- **Comment complex logic**
- **Update README** for new features
- **Add inline documentation** for new functions
- **Include usage examples**

## 🧪 Testing Guidelines

### Manual Testing
Since we don't have automated tests yet, please manually test:

1. **Core Functionality**
   - Upload different log file formats
   - Verify all analysis tabs work
   - Test with large files (100MB+)
   - Check error handling with malformed logs

2. **Web Interface**
   - Test all tabs and features
   - Verify visualizations render correctly
   - Check responsive behavior
   - Test export functionality

3. **Cross-Platform**
   - Test on Windows, Linux, macOS if possible
   - Verify launchers work correctly
   - Check file path handling

### Future Testing
We welcome contributions to add:
- Unit tests with pytest
- Integration tests
- Performance benchmarks
- Automated CI/CD pipeline

## 📊 Performance Considerations

### Memory Efficiency
- Use pandas chunking for large files
- Implement progress tracking with tqdm
- Clean up temporary data structures
- Monitor memory usage during development

### Processing Speed
- Optimize regex patterns
- Use efficient data structures
- Consider caching for repeated operations
- Profile code for bottlenecks

## 🛡️ Security Considerations

### Data Privacy
- **Never log sensitive information**
- **Sanitize examples** in documentation
- **Avoid hardcoded IPs** or server details
- **Test with sanitized data**

### Input Validation
- **Validate file uploads**
- **Handle malformed input gracefully**
- **Prevent path traversal attacks**
- **Limit resource consumption**

## 📖 Documentation

### Code Documentation
- **Docstrings** for all public functions
- **Type hints** where beneficial
- **Inline comments** for complex logic
- **README updates** for new features

### User Documentation
- **Clear installation instructions**
- **Usage examples**
- **Troubleshooting guides**
- **FAQ updates**

## 🎉 Pull Request Process

### Before Submitting
- [ ] Test changes locally
- [ ] Update documentation
- [ ] Check for conflicts with main branch
- [ ] Verify no sensitive data in commits
- [ ] Ensure code follows style guidelines

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tested locally
- [ ] Tested with large files
- [ ] Tested error handling
- [ ] Cross-platform testing (if applicable)

## Screenshots
(If UI changes are included)

## Additional Notes
Any additional information or considerations
```

### Review Process
1. **Automated checks** (future: CI/CD pipeline)
2. **Code review** by maintainers
3. **Testing verification**
4. **Documentation review**
5. **Merge when approved**

## 🏷️ Release Process

### Version Numbering
We use Semantic Versioning (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., 1.0.0)
- **Major** - Breaking changes
- **Minor** - New features, backward compatible
- **Patch** - Bug fixes, backward compatible

### Release Workflow
1. **Feature freeze** on develop branch
2. **Testing and bug fixes**
3. **Update version numbers**
4. **Update CHANGELOG**
5. **Merge to main**
6. **Create release tag**
7. **Publish release notes**

## 💬 Communication

### GitHub Issues
- **Use labels** to categorize issues
- **Reference related issues** and PRs
- **Update status** regularly
- **Close issues** when resolved

### Discussions
- **GitHub Discussions** for questions and ideas
- **Issue comments** for specific problems
- **PR reviews** for code-related feedback

## 🆘 Getting Help

### Documentation
- **README.md** - Installation and basic usage
- **SECURITY.md** - Security guidelines
- **PRIVACY.md** - Privacy information
- **Issues** - Browse existing problems and solutions

### Community
- **Create an issue** for bugs or feature requests
- **Start a discussion** for general questions
- **Check existing issues** before creating new ones

## 🎖️ Recognition

### Contributors
All contributors will be:
- **Acknowledged** in release notes
- **Listed** in future CONTRIBUTORS.md file
- **Credited** for their specific contributions
- **Invited** to provide input on project direction

### Types of Contributions Recognized
- Code contributions
- Documentation improvements
- Bug reports and testing
- Feature suggestions and feedback
- Community support and discussions

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## 🙏 Thank You

Thank you for considering contributing to the Nimble Streamer Log Analyzer! Your contributions help make this tool better for everyone in the streaming community.

---

**Questions?** Feel free to create an issue or start a discussion. We're here to help! 🚀
