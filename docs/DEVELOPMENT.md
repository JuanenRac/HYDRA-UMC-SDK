# Development rules

Start with schemas and fixtures, then write the smallest reference producer
and consumer. Generate clients only when the toolchain yields maintainable
output; otherwise use thin clients with contract tests.

Do not expose secrets in fixtures. Do not represent a physical action as a
fire-and-forget event. Contract changes require a changelog entry, compatibility
decision, examples, and tests in at least one producer and consumer.

## Current reference implementation

The Python client under `clients/python/` validates the normative v1 JSON
contracts without a runtime dependency. It is a reference validator, not a
transport client and not authorization for a physical command path.
