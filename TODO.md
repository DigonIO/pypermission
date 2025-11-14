# TODO

## Task IDs

- `xxxx?` Optional
- `xxxx.` Normal
- `xxxx!` Critical

Next ID: `34`

## Open Tasks

- `32.` Doc - Some docstrings do not list all possible reasons for raising an exception
- `29.` Doc Permission Design Guide -> As a subsection of RBAC system design
- `28.` Doc - Design Rationale: Reasoning for certain design decisions
- `27.` Doc - Add Auditing Guide
- `26?` Doc - Ensure closer alignment to style guide
- `22.` Doc - write [integration guide](https://pypermission.digon.io/guide/)
- `21.` Doc - Include external dependencies in build instead of using CDN
- `19.` Provide json/yaml import/export utility function
- `18.` Provide FastAPI standalone service with RBAC functionality via REST API
- `11.` Doc - Compare to ANSI (fix section 6/7 TODO)
- `10.` Doc - Compare to NIST

## Done Tasks

- `30!` README some SVGs are not available on PyPI, replace the relative path with URL to GitLab (main branch)
- `33.` CI - Include isort + black job
- `15.` Tests:
    - [x] Cover more than just next neighbor in role hierarchy tests.
        - [x] `role.ancestors`
        - [x] `role.descendants`
        - [x] `role.subjects`
        - [x] `role.check_permission`
        - [x] `role.assert_permission`
        - [x] `role.actions_on_resource`
        - [x] `role.permissions`
        - [x] `role.policies`
        - [x] `subject.roles`
        - [x] `subject.check_permission`
        - [x] `subject.actions_on_resource`
        - [x] `subject.policies`
        - [x] `subject.permissions`
    - [x] Test `Permission.__eq__` and `Permission.__neq__` methods method
    - [x] Test `Policy.__eq__` and `Policy.__neq__` methods method
- `25.` Add missing docstrings:
    - [x] `subject.actions_on_resource`, `role.actions_on_resource`
- `24.` Improve handling of psycopg errors in `process_subject_role_integrity_error` and `process_policy_integrity_error`
- `16.` Do not allow empty strings for `subject`, `role`, `action` and `resource_type` (`resource_id` is allowed to be empty)
    - [x] Implement tests
    - [x] Implement validation logic
- `23.` Doc - SEO and social description
- `20.` Doc - Include mkdocs socical card
- `9.` Doc - Finalize README
- `8.` Doc - Add CHANGELOG
- `3.` Decide for a seo optimal package name
- `2.` Setup Doc hosting environment
- `1.` CI/CD Pipeline
    - [x] Testing + Coverage
    - [x] Doc building
    - [x] Package publishing
    - [x] Doc publishing
- `17!` Ensure that optional dependencies (`psycopg`) are really optional
- `14.` Doc - Declare how we differentiate between ascendants/parents & descendants/children
- `13.` Doc - Start with FAQ
    - [x] Why we developed the library
    - [x] Can I implement Feature Flagging?
- `6.` Add Postgres as explicit dependency group
- `12.` Add missing functionality
    - [x] `RBAC.role.subjects` (`include_descendant_subjects` support)
    - [x] `RBAC.subject.roles` (`include_ascendant_roles` support)
    - [x] `RBAC.role.actions_on_resource`
    - [x] `RBAC.subject.actions_on_resource`
- `7.` Support for Sqlite & PostgreSQL IntegrityErrors
- `5.` Write Python docstrings
    - [x] RoleService
    - [x] SubjectService
    - [x] Util (plotting etc.)
    - [x] Misc.
- `4.` Testing
    - [x] Setup PyDocTest for markdown
    - [x] RoleService
    - [x] SubjectService
    - [x] Util (plotting etc.)
    - [x] Misc.
