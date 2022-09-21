# PyPermission

Lightweight permission system for your python projects.

## Example

Setup a permission authority and a helper function:

```py
from pypermission.json import Authority

auth = Authority()

def r(node: str):
    """Reduces boilerplate code while registering permission nodes."""
    return auth.register_permission(node=node)
```

Register permission nodes (example permission nodes from [towny](https://github.com/TownyAdvanced/Towny/blob/master/src/com/palmergames/bukkit/towny/permissions/PermissionNodes.java)):

```py
ROOT_ = auth.root_permission  # root
TOWNY_ = r("towny.*")  # parent
TOWNY_CHAT_ = r("towny.chat.*")  # parent
TOWNY_CHAT_TOWN = r("towny.chat.town")  # leave
TOWNY_CHAT_NATION = r("towny.chat.nation") # leave
TOWNY_CHAT_GLOBAL = r("towny.chat.global") # leave
TOWNY_WILD_ = r("towny.wild.*")  # parent
TOWNY_WILD_BUILD_ = r("towny.wild.build.*")  # parent
TOWNY_WILD_BUILD_X = r("towny.wild.build.<x>") # leave w/ payload
TOWNY_WILD_DESTROY_ = r("towny.wild.destroy.*")  # parent
TOWNY_WILD_DESTROY_X = r("towny.wild.destroy.<x>") # leave w/ payload
```

Create a group and add some permissions:

```py
GROUP_ID = "group_foo"  # the group ID can be str or int

auth.group_add(group_id=GROUP_ID)

auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_CHAT_)
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_BUILD_X, payload="dirt")
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_BUILD_X, payload="stone")
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_DESTROY_X, payload="iron")
auth.group_add_permission(group_id=GROUP_ID, permission=TOWNY_WILD_DESTROY_X, payload="gold")
```

Create a subject, add it to a group and add a permission:

```py
SUBJECT_ID = "user_bar"  # the subject ID can be str or int

auth.subject_add(subject_id=SUBJECT_ID)
auth.group_add_subject(group_id=GROUP_ID, subject_id=SUBJECT_ID)

auth.subject_add_permission(subject_id=SUBJECT_ID, permission=TOWNY_WILD_DESTROY_X, payload="diamond")

```

Now check if a subject has a desired permission:

```py
if(auth.subject_has_permission(subject_id=SUBJECT_ID, permission=TOWNY_CHAT_))
  ...  # permission provided by the group

if(auth.subject_has_permission(subject_id=SUBJECT_ID, permission=TOWNY_WILD_DESTROY_X, payload="diamond"))
  ...  # permission provided by the subject itself
```
