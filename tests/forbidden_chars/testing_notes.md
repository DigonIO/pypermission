# Testing Notes on forbidden characters

The tests for forbidden strings are split up for every definitional type. This enables us to work coverage reports on a per-type basis during the development in order to lock down as much of the api surface as needed. E.g. one can run:

```bash
uv run pytest --cov=src/pypermission/ tests/forbidden_chars/test_forbidden_role.py
uv run coverage html
```

And then spot where action is used in the api without being covered.
