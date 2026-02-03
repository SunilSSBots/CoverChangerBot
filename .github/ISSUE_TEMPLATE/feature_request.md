name: ✨ Feature Request
description: Suggest a new feature
title: "[FEATURE] "
labels: ["enhancement"]

body:
  - type: markdown
    attributes:
      value: |
        Great idea! Share your feature request to help us improve Video Cover Bot.

  - type: textarea
    id: description
    attributes:
      label: Feature Description
      description: Describe the feature you'd like to see
      placeholder: "It would be great if the bot could..."
    validations:
      required: true

  - type: textarea
    id: use_case
    attributes:
      label: Use Case
      description: Why would this feature be useful?
      placeholder: "This would help me because..."
    validations:
      required: true

  - type: textarea
    id: implementation
    attributes:
      label: Suggested Implementation (Optional)
      description: How do you think it could be implemented?
      placeholder: "The bot could..."

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: This feature doesn't already exist
          required: true
        - label: I've checked existing feature requests
          required: true
