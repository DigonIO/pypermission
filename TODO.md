# TODO

## Task IDs

* `xxxx?` Optional
* `xxxx.` Normal
* `xxxx!` Critical

Next ID: `17`

## Open Tasks

* `16` Do not allow empty strings for `subject`, `role`, `action` and `resource_type` (`resource_id` is allowed to be empty)
* `15` Tests: Cover more than just next neighbor in role hierarchy tests.
* `14` Doc - Declare how we differentiate between ascendants/parents & descendants/children
* `13` Doc - Start with FAQ
    * [ ] Why not Sessions?
    * [ ] How can I implement Feature Flagging?
* `12` Add missing functionality
    * [ ] `RBAC.role.subjects` (`include_descendant_subjects` support)
    * [ ] `RBAC.subject.roles` (`include_ascendant_roles` support)
    * [ ] `RBAC.role.actions_on_resource`
    * [ ] `RBAC.subject.actions_on_resource`
* `11` Doc - Compare to ANSI
* `10` Doc - Compare to NIST
* `9` Doc - Finalize README (and create better symlink name)
* `8` Doc - Add CHANGELOG
* `7` Support for Sqlite & PostgreSQL IntegrityErrors
* `6` Add Postgres as explicit dependency group
* `3` Decide for a seo optimal package name
* `2` Setup Doc hosting environment
* `1` CI/CD Pipeline
    * [ ] Testing + Coverage
    * [ ] Doc building
    * [ ] Package publishing
    * [ ] Doc publishing

## Done Tasks

* `5` Write Python docstrings
    * [x] RoleService
    * [x] SubjectService
    * [x] Util (plotting etc.)
    * [x] Misc.
* `4` Testing
    * [x] Setup PyDocTest for markdown
    * [x] RoleService
    * [x] SubjectService
    * [x] Util (plotting etc.)
    * [x] Misc.
