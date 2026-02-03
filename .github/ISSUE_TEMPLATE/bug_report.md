name: 🐛 Bug Report
description: Report a bug or issue
title: "[BUG] "
labels: ["bug"]

body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting a bug! Please fill out the form below to help us fix it quickly.

  - type: input
    id: title
    attributes:
      label: Bug Title
      description: A clear, concise description
      placeholder: "Bot not responding to /start command"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Detailed description of the bug
      placeholder: "When I send /start to the bot, it doesn't respond..."
    validations:
      required: true

  - type: textarea
    id: reproduce
    attributes:
      label: Steps to Reproduce
      description: Exact steps to reproduce the bug
      placeholder: |
        1. Send /start command
        2. Wait for 5 seconds
        3. Bot doesn't respond
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen instead?
      placeholder: "Bot should respond with main menu"
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Error Logs
      description: Any error messages or logs (use code block)
      placeholder: |
        ```
        [ERROR] Connection timeout
        [ERROR] Database connection failed
        ```

  - type: input
    id: environment
    attributes:
      label: Environment
      description: Where are you running the bot?
      placeholder: "Docker / VPS / Heroku / Local"

  - type: input
    id: python_version
    attributes:
      label: Python Version
      description: Python version you're using
      placeholder: "3.9 / 3.10 / 3.11"

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I've checked existing issues
          required: true
        - label: I've followed the setup guide
          required: true
        - label: I've provided all required information
          required: true
