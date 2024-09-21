# bingbustools

Tools for Binghamton buses.

Setup:

```
pdm install --dev
```

Lint + format:

```
eval $(pdm venv activate) # only needs to be done once
ruff check
ruff format
mypy .
```

Add new dependency:

```
pdm add <PACKAGE>
```
