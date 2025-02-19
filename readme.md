# Design Patterns POC

A project demonstrating various design patterns.

## Setup

This project uses `uv` as its Python package manager.

### Installing uv

#### On Windows (using curl)

```cmd
curl -LsSf https://astral.sh/uv/install.ps1 | powershell
```

#### On Linux/macOS (using curl)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Verify installation:

```
uv --version
```

### Project Setup

1. Clone the repository

   ```
   git clone https://github.com/anmolg-ebbo/design_pattern_poc.git
   cd design_pattern_poc
   ```

2. Sync dependencies:
   ```
   uv sync
   ```
   This will read your project dependencies from pyproject.toml and install them.

## Running the Project

To start the development server:

```
uv run main.py
```
