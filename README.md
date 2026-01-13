<!---
################################################################
#                                                              #
#  This file is part of HermesBaby                             #
#                       the software engineer's typewriter     #
#                                                              #
#      https://github.com/hermesbaby                           #
#                                                              #
#  Copyright (c) 2024 Alexander Mann-Wahrenberg (basejumpa)    #
#                                                              #
#  License(s)                                                  #
#                                                              #
#  - MIT for contents used as software                         #
#  - CC BY-SA-4.0 for contents used as method or otherwise     #
#                                                              #
################################################################
-->

# HermesBaby

The Software and Systems Engineers' Typewriter

Meant to be the authoring environment to get our work done.

## Purpose

## Using HermesBaby to Enable Docs-as-Code in Corporate Environments

HermesBaby provides a curated toolbox and clean command-line interface that operationalizes the Docs-as-Code approach across engineering organizations. It is designed to simplify both the **authoring experience for engineers** and the **integration into corporate environments** — including CI/CD, documentation portals, and internal security policies.

For document authors, HermesBaby makes Docs-as-Code accessible:

- Projects are scaffolded from templates in seconds.
- Authoring happens in the same environment used for code development.
- Build, preview, and publish commands are cleanly separated and easy to use.
- Kconfig-based configuration offers clarity and traceability without clutter.

At the same time, HermesBaby is built for integration at scale:

- It works seamlessly with **CI pipelines** and version-controlled repositories.
- It supports **custom toolchains** and validates external dependencies automatically.
- It installs and configures required build tools, linters, and extensions — even in headless or air-gapped environments.
- It ensures predictable and compliant deployments via SSH-based publishing and access control via `.htaccess`.

HermesBaby doesn't just promote structured authoring — it makes documentation **controllable**, **auditable**, and **cyber-secure**. Its infrastructure-aware design allows teams to:

- Verify toolchains before use.
- Lock down deployment keys and paths.
- Comply with internal policies and regulatory requirements.

By lowering the barrier to entry for engineers while raising the bar on control and compliance, HermesBaby bridges the cultural and technical gap between **grassroots Docs-as-Code practices** and **enterprise-grade documentation workflows**.

## Installation

Two options are available: System-wide or project-wise

### System-wide

While it's possible to install it globally via `pip`, it's recommended to install it via `pipx` to keep your system clean and tidy since `hermesbaby` brings many Python packages with it.

```bash
python3 -m pip install pipx
python3 -m pipx install hermesbaby
```

### Project-wise

Let's assume your project is managed with Poetry you would add `hermesbaby` similar to

```bash
poetry add hermesbaby
```

or

```bash
poetry add hermesbaby --group dev
```

## First usage

Close the gaps by installing the missing tools. You may use the help hermesbaby gave you to do so.

Beside `hermesbaby` there is a second, shorter alias:

```bash
hb
```

Check environment for prerequisites

```bash
hb check tools
```

Start your first new virtual piece of writing

```bash
hb new --template arc42
cd arc42
hb html-live
```

CTRL-C.

Start editing

```bash
git init .
code .
```

Click Statusbar / html-live

Apply changes to some `docs/*/index.md` ... and so on.

Happy coding specifications ;-) "

## Development and Testing

### Running End-to-End (E2E) Tests

The E2E tests are written using [BATS](https://github.com/bats-core/bats-core). To run them manually, ensure you have the project dependencies installed via Poetry.

#### Windows (Git Bash)

```bash
poetry run bash ./tests/e2e/bats/bin/bats tests/e2e/
```

#### Linux / macOS

```bash
poetry run tests/e2e/bats/bin/bats tests/e2e/
```
