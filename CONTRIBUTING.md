# Contributing to IQ Option API

Thank you for your interest in contributing to the IQ Option API project! Your contributions help make this project better for everyone.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Any relevant error messages

### Suggesting Features

We welcome feature suggestions! Please open an issue with:

- Clear description of the proposed feature
- Use cases and examples
- Benefits to users

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Test your changes thoroughly
4. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```
5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request**

## 📝 Code Style Guidelines

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex algorithms
- Keep functions focused and small

### Example

```python
def get_candles_with_limit(self, asset, interval, count, endtime):
    """
    Retrieve historical candlestick data with error handling.
    
    Args:
        asset (str): Asset name (e.g., 'EURUSD')
        interval (int): Candle interval in seconds
        count (int): Number of candles to retrieve
        endtime (int): End timestamp
        
    Returns:
        list: List of candle dictionaries or None on error
    """
    try:
        return self.api.get_candles(asset, interval, count, endtime)
    except Exception as e:
        logging.error(f"Error retrieving candles: {e}")
        return None
```

## 🧪 Testing

Before submitting, please:

1. Test your code with different scenarios
2. Verify it works with PRACTICE account
3. Check for edge cases
4. Ensure no new warnings or errors

## 📦 Adding Examples

When adding examples:

- Place in `examples/` directory
- Add proper error handling
- Include warnings about trading risks
- Use PRACTICE account by default
- Document what the example demonstrates

## 🔒 Security

- **Never commit credentials or API keys**
- Sanitize any data in examples
- Use environment variables for sensitive info
- Review data handling for security issues

## 📚 Documentation

When adding features:

- Update README.md if needed
- Add docstrings to new functions
- Update examples if API changes
- Document any breaking changes

## 🐛 Bug Fixes

For bug fixes:

- Clearly describe the bug being fixed
- Reference related issues
- Add tests if possible
- Verify fix works in multiple scenarios

## ❓ Questions?

Feel free to open an issue for any questions about contributing.

## 🙏 Thank You

Your contributions are greatly appreciated! Every improvement helps the community.

---

**Note**: By contributing, you agree that your contributions will be licensed under the same license as the project.

