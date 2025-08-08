# Contributing to Dream Recorder

Thank you for your interest in contributing to Dream Recorder! We welcome contributions from the community.

## How to Contribute

### Reporting Issues
- Check if the issue already exists
- Include steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include relevant error messages and logs

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Add tests if applicable
   - Update documentation as needed
4. **Test your changes**
   ```bash
   # Run the application locally
   docker compose up
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add: Brief description of change"
   ```
6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines
- Python: Follow PEP 8
- JavaScript: Use consistent indentation (2 spaces)
- Comment complex logic
- Keep functions focused and small

### Areas We Need Help
- 🐛 Bug fixes
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- 🌍 Internationalization
- ⚡ Performance optimizations
- 🧪 Test coverage

### Development Setup

1. Clone your fork
   ```bash
   git clone https://github.com/YOUR_USERNAME/dream-recorder.git
   cd dream-recorder
   ```

2. Copy and configure environment
   ```bash
   cp .env.example .env
   cp config.example.json config.json
   # Edit both files with your API keys
   ```

3. Run with Docker
   ```bash
   docker compose up
   ```

### Questions?
Feel free to open an issue for discussion or reach out through GitHub discussions.

## License
By contributing, you agree that your contributions will be licensed under the MIT License.