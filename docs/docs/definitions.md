# PyPermission - Formal Definitions

In PyPermission, the core concepts for Role Based Access Control (**RBAC**) are defined as follows:

| Type | Description |
| - | - |
| **Subject** | Represents a user or other objects that require Permission checks. |
| **Role** | A collection of Permissions a Subject can be assigned to. Roles can inherit Permissions from parent Roles. |
| **ResourceType** | The type of a Resource (e.g. folder, document or event). |
| **ResourceID** | A unique identifier for a specific instance of a resource (e.g. filename, INT or UUID). |
| **Action** | An operation that can be performed on a resource (e.g., create, edit or delete). |

Each type in the table inherits from `str`, meaning they only exist as string representations through the rbac API. The **ResourceID** feature allows the value `*` to act as a wildcard representing all potential **ResourceID** values.

Formally **Resource**, **Permission** and **Policy** can be defined as following:

\[
\begin{aligned}
\text{Resource}   & := \bigl(\text{resource\_type} : \text{ResourceType},\; \text{resource\_id} : \text{ResourceID} \bigr) \\[2mm]
\text{Permission} & := \bigl(\text{resource} : \text{Resource},\; \text{action} :  \text{Action}\bigr) \\[2mm]
\text{Policy}     & := \bigl(\text{role} : \text{Role},\; \text{permission} :  \text{Permission}\bigr) \\
\end{aligned}
\]

In this model, a **Resource** is any object that can be acted upon, a **Permission** links an **Action** to a **Resource**, and a **Policy** assigns one or more **Permissions** to a **Role**.

## Role Hierarchy: Parents, Children, Ancestors, and Descendants

The library distinguishes between **direct** (immediate) and **indirect** (transitive) hierarchical **Role** relationships using four core terms:

| Term           | Definition                                                          | Implementation Reference                    |
| -------------- | ------------------------------------------------------------------- | ------------------------------------------- |
| **Parent**     | A direct ascendant **Role** (immediate superior).                       | `RoleService.parents(role: str) -> str`     |
| **Child**      | A direct descendant **Role** (immediate inferior).                      | `RoleService.children(role: str) -> str`    |
| **Ancestor**   | All ascendant **Roles** (direct + indirect, e.g., parent, grandparent). | `RoleService.ancestors(role: str) -> str`   |
| **Descendant** | All descendant **Roles** (direct + indirect, e.g., child, grandchild).  | `RoleService.descendants(role: str) -> str` |

!!! note

    Some RBAC libraries use alternative terms for direct relationships:

    - **Predecessor** = Parent (direct ascendant).
    - **Successor** = Child (direct descendant).
