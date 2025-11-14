# HowTo: Contribute to PyPermission

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
uv run pytest --markdown-docs --markdown-docs-syntax=superfences docs/docs
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

## Static analysis

Run mypy with:

```console
uv run mypy src
```

Run ruff with:

```console
uv run ruff check src
```

## Style Guide

### Docs

When describing the library for example in the following permission check:

```py
RBAC.subject.assert_permission(
        subject="Ursula",
        permission=Permission(resource_type="event", resource_id="group:123", action="view"),
        db=db,
    )
```

The documentation should use the following markup in descriptions:

* Library types and classes should be written in `PascalCase` and bold (for example `**Permission**` -> **Permission**)
* Definitional types (those that do not have a corresponding class or type in the library, such as **Role** or **Subject**) should be written in `PascalCase` and bold (just like Library types)
* Stay close to the definitions in `docs/docs/definitions.md` (e.g. **ResourceType** instead of "resource type",
  **ResourceID** instead of "resource ID"). Infer from the definitions, that for consistency reasons **RoleID** should be preferred over "role id" even though not explicitly stated.
* values should be written in code blocks (for example `Alex`, `19`, `view` or `group:123`)
* application level types (like `event` or `group`) should be treated as values
* attributes should be written in code blocks and in `snake_case` (for example `resource_type`, `resource_id`)

Examples:

<https://pypermission.digon.io/definitions/>

* "ResourceType" instead of "Resource type"