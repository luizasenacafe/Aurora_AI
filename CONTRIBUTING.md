# Contributing

Use English for issues, pull requests, and documentation. The current UI is primarily Brazilian Portuguese; coordinate localization rather than mixing languages within a screen.

1. Read the architecture and privacy documents.
2. Keep each change focused.
3. Use a virtual environment and relevant requirements.
4. Run the README checks. Check mobile, desktop, keyboard access, and reduced motion for UI changes.
5. Describe the problem, resulting behavior, validation, and limitations in the pull request.

Never commit tokens, model weights, local databases, logs, or live configuration. Use temporary stores and simulated upstream responses. Preserve protocol/data compatibility unless a migration is supplied.

The Electron prototype is historical. Target current web or Python code for new features. Do not present mocked inference as a real model test.
