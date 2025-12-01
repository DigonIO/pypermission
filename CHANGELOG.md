# Changelog

## 0.4.1

### Bugfixes

- FIX: resource_type validator giving misleading error message on bracket imbalance

## 0.4.0

### API Changes

- `pypermission.service.role.RoleService.ancestors` renamed to `pypermission.service.role.RoleService.ascendants`
- Disallowed certain strings in definitional type
    - Strings `"*"` and `""` are only allowed in ResourceID
    - `:` can never be used
    - The characters `[` and `]` are not allowed anywhere inside ResourceType
    - Leading & trailing spaces are never allowed
    - Brackets `[` and `]` must be balanced.

## 0.3.0

### API Changes

- `subject`, `role`, `action` and `resource_type` are no longer allowed to be empty strings

### Misc

- General documentation improvements
- General testing improvements + additional coverage
- Include `isort` and `black` in CI workflow
- Improved error handling

## 0.2.1

### Bugfixes

- FIX: Correctly manage optional postgres and util dependencies

### Misc

- README: Add PyPI and pepy.tech badges.

## 0.2.0

- Initial beta release.
