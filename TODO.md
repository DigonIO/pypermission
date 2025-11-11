# TODO

## Task IDs

- `xxxx?` Optional
- `xxxx.` Normal
- `xxxx!` Critical

Next ID: `22`

## Open Tasks

- `22` Doc - write [integration guide](https://pypermission.digon.io/)guide/
- `21` Doc - Include external dependencies in build instead of using CDN
- `20` Doc - Include mkdocs socical card
- `19` Provide json/yaml import/export utility function
- `18` Provide FastAPI standalone service with RBAC functionality via REST API
- `16` Do not allow empty strings for `subject`, `role`, `action` and `resource_type` (`resource_id` is allowed to be empty)
- `15` Tests: Cover more than just next neighbor in role hierarchy tests.
- `11` Doc - Compare to ANSI (fix section 6/7 TODO)
- `10` Doc - Compare to NIST
- `9` Doc - Finalize README

## Done Tasks

- `8` Doc - Add CHANGELOG
- `3` Decide for a seo optimal package name
- `2` Setup Doc hosting environment
- `1` CI/CD Pipeline
    - [x] Testing + Coverage
    - [x] Doc building
    - [x] Package publishing
    - [x] Doc publishing
- `17!` Ensure that optional dependencies (`psycopg`) are really optional
- `14` Doc - Declare how we differentiate between ascendants/parents & descendants/children
- `13` Doc - Start with FAQ
    - [x] Why we developed the library
    - [x] Can I implement Feature Flagging?
- `6` Add Postgres as explicit dependency group
- `12` Add missing functionality
    - [x] `RBAC.role.subjects` (`include_descendant_subjects` support)
    - [x] `RBAC.subject.roles` (`include_ascendant_roles` support)
    - [x] `RBAC.role.actions_on_resource`
    - [x] `RBAC.subject.actions_on_resource`
- `7` Support for Sqlite & PostgreSQL IntegrityErrors
- `5` Write Python docstrings
    - [x] RoleService
    - [x] SubjectService
    - [x] Util (plotting etc.)
    - [x] Misc.
- `4` Testing
    - [x] Setup PyDocTest for markdown
    - [x] RoleService
    - [x] SubjectService
    - [x] Util (plotting etc.)
    - [x] Misc.
