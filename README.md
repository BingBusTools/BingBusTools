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

## Development Tasks

Add new dependency: (add `-d` for dev)

```
pdm add <PACKAGE>
```

Generate protobuf code: (requires `protoc`)

```
protoc --proto_path=src/protobuf --python_out=src/protobuf src/protobuf/gtfs-realtime.proto
```
