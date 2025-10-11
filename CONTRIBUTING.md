# HowTo: Contribute to pypermission

## Development setup

Install dependencies

```console
uv sync --all-groups
```

To run the postgres database with docker, first create the `.env` file at `docker/.env` and set the required variables based on the `docker/.env.template` file. Then:

```console
cd docker
docker compose up
```

## Testing

### Standard tests

```console
uv run pytest --cov=src/pypermission/ tests
```

### Doc tests

```console
uv run pytest --markdown-docs docs/docs
```

## Visual coverage report

Generate the html coverage report. The command creates a folder `htmlcov` with an `index.html` as landing page.

```console
uv run coverage html
```

## Documentation

Serve the documentation for easy local development.

```console
uv run mkdocs serve -f docs/mkdocs.yml
```

Build the documentation.

```console
uv run mkdocs build -f docs/mkdocs.yml
```
