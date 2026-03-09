export const starterSuite = `version: "0.1"
name: Support Ticket Routing
description: Evaluate whether the prompt routes support tickets into the right queue.
models:
  - gpt-4o
  - gpt-4.1
tags:
  - support
  - classification
prompt:
  system: |
    You are a support triage assistant. Read the ticket and output JSON with keys
    "queue" and "priority". Keep the response compact and deterministic.
  user: |
    Ticket:
    {{ticket}}

    Customer tier: {{tier}}
assertions:
  - id: queue-match
    type: contains
    expected: '"queue": "{{expected_queue}}"'
judge:
  - id: policy
    name: Policy adherence
    rubric: Reward outputs that choose the correct queue and avoid hallucinated fields.
cases:
  - id: billing-upgrade
    description: Enterprise billing change request
    inputs:
      ticket: "We need 20 more seats added before renewal next week."
      tier: enterprise
      expected_queue: billing
  - id: security-incident
    description: Suspected security issue
    inputs:
      ticket: "We saw unknown logins from two countries overnight. Please investigate."
      tier: enterprise
      expected_queue: security
`;

