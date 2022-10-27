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
    TOWNY_WILD_DESTROY_ = "towny.wild.destroy.*"
    TOWNY_WILD_DESTROY_X = "towny.wild.destroy.<x>"
```

```yaml
groups:
  parent_group:
    member_groups:
      - child_group
    permission_nodes:
      - towny.chat.*
      - towny.wild.*
  child_group:
    member_subjects:
      - user
    permission_nodes:
      - towny.chat.town
      - towny.wild.build.<iron>
subjects:
  user:
    permission_nodes:
      - towny.build.*
```


```txt
- towny.chat.*: parent_group
- towny.wild.*: parent_group
- towny.build.*: user
```