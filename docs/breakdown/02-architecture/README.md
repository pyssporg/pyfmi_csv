---
id: INFO-002
type: info
title: Architecture
summary: Architecture overview
date: 2026-11-11
status: current
---

# Architecture

- `src/pyfmu_csv/` — Python package
- `src/runtime/` — Native FMI runtime
- `containers/` — Container build
- `INFO-004` [modelDescription emission](modeldescription-emission.md) — the XML writer uses the optional `pyfmi_interfaces` extra and keeps a bundled zero-dependency fallback.
