```py
class TownyPermissionNode(PermissionNode):
    # Permission nodes for testing inspired be the towny permission nodes
    # https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java
    TOWNY_ = "towny.*"
    TOWNY_CHAT_ = "towny.chat.*"
    TOWNY_CHAT_TOWN = "towny.chat.town"
    TOWNY_CHAT_NATION = "towny.chat.nation"
    TOWNY_CHAT_GLOBAL = "towny.chat.global"
    TOWNY_WILD_ = "towny.wild.*"
    TOWNY_WILD_BUILD_ = "towny.wild.build.*"
    TOWNY_WILD_BUILD_X = "towny.wild.build.<x>"
    TOWNY_WILD_BUILD_IRON = "towny.wild.build.iron"
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"
```

```yaml
groups:
  parent_group:
    member_groups:
      - child_group
    permission_nodes:
      towny.chat.*: Null
      towny.wild.*: Null
  child_group:
    member_subjects:
      - user
    permission_nodes:
      towny.chat.town: Null
      towny.wild.build.<x>: ["iron"]
      towny.wild.build.iron: Null
subjects:
  user:
    permission_nodes:
      towny.build.*: Null
permission_nodes:
  towny.chat.*:
    towny.chat.town: Null
    towny.chat.global: Null
    towny.chat.nation: Null
  towny.wild.*:
    towny.wild.build.*:
      towny.wild.build.<x>: []
      towny.wild.build.iron: Null
    towny.wild.destroy.*:
      towny.wild.destroy.<x>: []
  towny.chat.town: Null
  towny.wild.build.<x>: ["iron"]
  towny.wild.build.iron: Null
```

```yaml
permission_nodes:
  t
```

```yaml
permission_nodes:
  towny.*:
    towny.chat.*:
  towny.chat.*:
    - towny.chat.town
    - towny.chat.global
    - towny.chat.nation
    - towny.chat.foo.*
  towny.chat.foo.*:
    - ddd
  towny.chat.town: []
```

```txt
- towny.chat.*: user->child_group->parent_group
- towny.wild.*: user->child_group->parent_group
- towny.wild.build.<iron>: user->child_group
- towny.build.*: user
- towny.chat.town: user->child_group
```

```txt
- towny.chat.*: parent_group
- towny.wild.*: parent_group
- towny.build.*: user
```
