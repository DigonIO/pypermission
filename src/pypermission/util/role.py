import networkx as nx
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from pypermission.exc import PyPermissionError
from pypermission.models import HierarchyORM, MemberORM, Permission, PolicyORM, RoleORM

################################################################################
#### Role dag tools
################################################################################


def role_dag(
    *,
    root_roles: set[str] | None = None,
    include_subjects: bool = True,
    include_permissions: bool = True,
    db: Session,
) -> nx.DiGraph:
    """
    Generate a directed acyclic graph (DAG) that reflects the role hierarchy
    from the viewpoint of the `root_roles`.
    By definition, the resulting DAG does **not** contain any roles that are
    descendants of those root roles.

    Parameters
    ----------
    root_roles : set[str] | None
        Root Roles of the generated DAG. If its None, all existing Roles will be included.
    include_subjects : bool
        Include assigned Subjects in the DAG.
    include_permissions : bool
        Include granted Permissions in the DAG.

    Returns
    -------
    nx.DiGraph
        The generated DAG.
    """
    roles, hierarchies = _get_roles_and_hierarchies(root_roles=root_roles, db=db)

    dag = nx.DiGraph()
    dag.add_nodes_from(roles, type="role_node")
    dag.add_edges_from(hierarchies, type="hierarchy_edge")

    if include_subjects:
        subjects, members = _get_subjects_and_members(roles=roles, db=db)
        dag.add_nodes_from(subjects, type="subject_node")
        dag.add_edges_from(members, type="member_edge")

    if include_permissions:
        subjects, members = _get_permissions_and_polices(roles=roles, db=db)
        dag.add_nodes_from(subjects, type="permission_node")
        dag.add_edges_from(members, type="policy_edge")

    return dag


################################################################################
#### Util
################################################################################


def _get_roles_and_hierarchies(
    *, root_roles: set[str] | None, db: Session
) -> tuple[set[str], set[tuple[str, str]]]:
    if root_roles is None:
        role_orms = db.scalars(select(RoleORM)).all()
        roles = set(role_orm.id for role_orm in role_orms)

        hierarchy_orms = db.scalars(select(HierarchyORM)).all()
        hierarchies = set(
            (hierarchy_orm.parent_role_id, hierarchy_orm.child_role_id)
            for hierarchy_orm in hierarchy_orms
        )
        return roles, hierarchies

    role_ormes = db.scalars(select(RoleORM).where(RoleORM.id.in_(root_roles))).all()
    roles = set(role_orme.id for role_orme in role_ormes)

    if unknown_roles := root_roles ^ roles:
        if len(unknown_roles) == 1:
            raise PyPermissionError(f"Requested role does not exist: {unknown_roles}!")
        else:
            raise PyPermissionError(f"Requested roles do not exist: {unknown_roles}!")

    root_cte = (
        select(HierarchyORM)
        .where(HierarchyORM.child_role_id.in_(root_roles))
        .cte(name="root_cte", recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM).where(
            HierarchyORM.child_role_id == traversing_cte.c.parent_role_id
        )
    )

    ancestor_relations = db.execute(
        select(relations_cte.c.parent_role_id, relations_cte.c.child_role_id)
    ).all()

    roles = root_roles | {role for pair in ancestor_relations for role in pair}
    hierarchies = set(ancestor_relations)  # type: ignore

    return roles, hierarchies


def _get_subjects_and_members(
    *, roles: set[str], db: Session
) -> tuple[set[str], set[tuple[str, str]]]:

    member_orms = db.scalars(
        select(MemberORM).where(MemberORM.role_id.in_(roles))
    ).all()
    members = set(
        (member_orm.role_id, member_orm.subject_id) for member_orm in member_orms
    )

    subjects = {member_orm.subject_id for member_orm in member_orms}

    return subjects, members


def _get_permissions_and_polices(
    *, roles: set[str], db: Session
) -> tuple[set[str], set[tuple[str, str]]]:

    policy_orms = db.scalars(
        select(PolicyORM).where(PolicyORM.role_id.in_(roles))
    ).all()
    policies = set(
        (
            policy_orm.role_id,
            str(
                Permission(
                    resource_type=policy_orm.resource_type,
                    resource_id=policy_orm.resource_id,
                    action=policy_orm.action,
                )
            ),
        )
        for policy_orm in policy_orms
    )

    permissions = set(policy[1] for policy in policies)

    return permissions, policies
