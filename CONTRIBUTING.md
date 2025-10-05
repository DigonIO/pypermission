# HowTo: Contribute to pypermission

## Development setup

```console
uv sync
```

## Testing

```console
uv run pytest --cov=src/pypermission/ tests
```

## Visual coverage report

Generate the html coverage report. The command creates a folder `htmlcov` with an `index.html` as landing page.

```console
uv run coverage html
```

## Documentation

Build the documentation.

```console
uv run mkdocs build
```

Serve the documentation for easy local development.

```console
uv run mkdocs serve
```
