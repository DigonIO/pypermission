# HowTo: Contributing

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
