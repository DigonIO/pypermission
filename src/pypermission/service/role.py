from collections.abc import Sequence

from sqlalchemy.sql import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.models import (
    Permission,
    RoleORM,
    HierarchyORM,
    PolicyORM,
    FrozenClass,
    MemberORM,
    Policy,
)
from pypermission.util.role import _permission_to_str
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### RoleService
################################################################################


class RoleService(metaclass=FrozenClass):

    @classmethod
    def create(cls, *, role: str, db: Session) -> None:
        """
        Create a new role .

        Parameters
        ----------
        role : str
            The ID of the role to create.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a role with the given ID already exists.
        """
        try:
            role_orm = RoleORM(id=role)
            db.add(role_orm)
            db.flush()
        except IntegrityError:
            db.rollback()
            raise PyPermissionError(f"The role '{role}' already exists!")

    @classmethod
    def delete(cls, *, role: str, db: Session) -> None:
        """
        Delete an existing role.

        Parameters
        ----------
        role : str
            The ID of the role to delete.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a role with the given ID does not exist.
        """
        role_orm = db.get(RoleORM, role)
        if role_orm is None:
            raise PyPermissionError(f"An unknown role '{role}' cannot be deleted!")
        db.delete(role_orm)
        db.flush()

    @classmethod
    def list(cls, *, db: Session) -> tuple[str, ...]:
        """
        Retrieve all roles currently defined.

        Parameters
        ----------
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str]
            A tuple containing the IDs of all roles.
        """
        role_orms = db.scalars(select(RoleORM)).all()
        return tuple(role_orm.id for role_orm in role_orms)

    @classmethod
    def add_hierarchy(cls, *, parent_role: str, child_role: str, db: Session) -> None:
        """
        Add a parent-child relationship between two roles.

        Parameters
        ----------
        parent_role : str
            The ID of the parent role.
        child_role : str
            The ID of the child role.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If the parent and child roles are the same.
            If one or both roles do not exist in the system.
            If adding the hierarchy would create a loop.
        IntegrityError
            If a database integrity issue occurs while adding the hierarchy.
        """
        if parent_role == child_role:
            raise PyPermissionError(f"Both roles '{parent_role}' must not be the same!")

        roles = db.scalars(
            select(RoleORM.id).where(RoleORM.id.in_([parent_role, child_role]))
        ).all()
        if len(roles) == 1:
            missing_role = child_role if parent_role in roles else parent_role
            raise PyPermissionError(f"Role '{missing_role}' does not exist!")
        elif len(roles) == 0:
            raise PyPermissionError(
                f"Roles '{parent_role}' and '{child_role}' do not exist!"
            )

        root_cte = (
            select(HierarchyORM)
            .where(HierarchyORM.parent_role_id == child_role)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM).where(
                HierarchyORM.parent_role_id == traversing_cte.c.child_role_id
            )
        )

        critical_leaf_relations = db.execute(
            select(relations_cte).where(relations_cte.c.child_role_id == parent_role)
        ).all()

        if critical_leaf_relations:
            raise PyPermissionError("The desired hierarchy would generate a loop!")

        try:
            hierarchy_orm = HierarchyORM(
                parent_role_id=parent_role, child_role_id=child_role
            )
            db.add(hierarchy_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            raise PyPermissionError(
                f"The hierarchy '{parent_role}' -> '{child_role}' exists!"
            )

    @classmethod
    def remove_hierarchy(
        cls, *, parent_role: str, child_role: str, db: Session
    ) -> None:
        """
        Remove a parent-child relationship between two roles.

        Parameters
        ----------
        parent_role : str
            The ID of the parent role.
        child_role : str
            The ID of the child role.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If the parent and child roles are the same.
            If one or both roles do not exist in the system.
            If adding the hierarchy would create a loop.
        IntegrityError
            If a database integrity issue occurs while adding the hierarchy.
        """
        if parent_role == child_role:
            raise PyPermissionError(f"Both roles '{parent_role}' must not be the same!")

        hierarchy_orm = db.get(HierarchyORM, (parent_role, child_role))
        if hierarchy_orm is None:
            roles = db.scalars(
                select(RoleORM.id).where(RoleORM.id.in_([parent_role, child_role]))
            ).all()
            if len(roles) == 1:
                missing_role = child_role if parent_role in roles else parent_role
                raise PyPermissionError(f"Role '{missing_role}' does not exist!")
            elif len(roles) == 0:
                raise PyPermissionError(
                    f"Roles '{parent_role}' and '{child_role}' do not exist!"
                )
            else:
                raise PyPermissionError(
                    f"The hierarchy '{parent_role}' -> '{child_role}' does not exists!"
                )

        db.delete(hierarchy_orm)
        db.flush()

    @classmethod
    def parents(cls, *, role: str, db: Session) -> tuple[str, ...]:
        parents = db.scalars(
            select(HierarchyORM.parent_role_id).where(
                HierarchyORM.child_role_id == role
            )
        ).all()
        if len(parents) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        return tuple(parents)

    @classmethod
    def children(cls, *, role: str, db: Session) -> tuple[str, ...]:
        children = db.scalars(
            select(HierarchyORM.child_role_id).where(
                HierarchyORM.parent_role_id == role
            )
        ).all()
        if len(children) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        return tuple(children)

    @classmethod
    def ancestors(cls, *, role: str, db: Session) -> tuple[str, ...]:
        root_cte = (
            select(HierarchyORM)
            .where(HierarchyORM.child_role_id == role)
            .cte(name="root_cte", recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM).where(
                HierarchyORM.child_role_id == traversing_cte.c.parent_role_id
            )
        )

        ancestor_relations = (
            db.scalars(select(relations_cte.c.parent_role_id)).unique().all()
        )

        if len(ancestor_relations) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        return tuple(ancestor_relations)

    @classmethod
    def descendants(cls, *, role: str, db: Session) -> tuple[str, ...]:
        root_cte = (
            select(HierarchyORM)
            .where(HierarchyORM.parent_role_id == role)
            .cte(name="root_cte", recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM).where(
                HierarchyORM.parent_role_id == traversing_cte.c.child_role_id
            )
        )

        descendant_relations = (
            db.scalars(select(relations_cte.c.child_role_id)).unique().all()
        )

        if len(descendant_relations) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        return tuple(descendant_relations)

    @classmethod
    def subjects(cls, *, role: str, db: Session) -> tuple[str, ...]:
        # TODO raise IntegrityError if role is unknown and if possible via ORM
        subjects = db.scalars(
            select(MemberORM.subject_id).where(MemberORM.role_id == role)
        ).all()
        if len(subjects) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role ('{role}') does not exist!")
        return tuple(subjects)

    @classmethod
    def grant_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        try:
            policy_orm = PolicyORM(
                role_id=role,
                resource_type=permission.resource_type,
                resource_id=permission.resource_id,
                action=permission.action,
            )
            db.add(policy_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            p_str = _permission_to_str(
                resource_type=permission.resource_type,
                resource_id=permission.resource_id,
                action=permission.action,
            )
            raise PyPermissionError(f"The Permission '{p_str}' does already exist!")

    @classmethod
    def revoke_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        policy_tuple = (
            role,
            permission.resource_type,
            permission.resource_id,
            permission.action,
        )
        policy_orm = db.get(
            PolicyORM,
            policy_tuple,
        )
        if policy_orm is None:
            p_str = _permission_to_str(
                resource_type=permission.resource_type,
                resource_id=permission.resource_id,
                action=permission.action,
            )
            raise PyPermissionError(f"The Permission '{p_str}' does not exist!")

        db.delete(policy_orm)
        db.flush()

    @classmethod
    def check_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> bool:
        root_cte = (
            select(RoleORM.id.label("role_id"))
            .where(RoleORM.id == role)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM.parent_role_id).where(
                HierarchyORM.child_role_id == traversing_cte.c.role_id
            )
        )
        policy_orms = db.scalars(
            select(PolicyORM)
            .join(relations_cte, PolicyORM.role_id == relations_cte.c.role_id)
            .where(
                PolicyORM.resource_type == permission.resource_type,
                PolicyORM.resource_id.in_((permission.resource_id, "*")),
                PolicyORM.action == permission.action,
            )
        ).all()

        return len(policy_orms) > 0

    @classmethod
    def assert_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        if not cls.check_permission(role=role, permission=permission, db=db):
            p_str = _permission_to_str(
                resource_type=permission.resource_type,
                resource_id=permission.resource_id,
                action=permission.action,
            )
            raise PyPermissionNotGrantedError(
                f"Permission '{p_str}' is not granted for Role '{role}'!"
            )

    @classmethod
    def permissions(
        cls,
        *,
        role: str,
        inherited: bool = True,
        db: Session,
    ) -> tuple[Permission, ...]:
        policy_orms = get_policy_orms_for_role(role=role, inherited=inherited, db=db)

        return tuple(
            Permission(
                resource_type=policy_orm.resource_type,
                resource_id=policy_orm.resource_id,
                action=policy_orm.action,
            )
            for policy_orm in policy_orms
        )

    @classmethod
    def policies(
        cls,
        *,
        role: str,
        inherited: bool = True,
        db: Session,
    ) -> tuple[Policy, ...]:
        policy_orms = get_policy_orms_for_role(role=role, inherited=inherited, db=db)

        return tuple(
            Policy(
                role=role,
                permission=Permission(
                    resource_type=policy_orm.resource_type,
                    resource_id=policy_orm.resource_id,
                    action=policy_orm.action,
                ),
            )
            for policy_orm in policy_orms
        )


################################################################################
#### Util
################################################################################


def get_policy_orms_for_role(
    *, role: str, inherited: bool = True, db: Session
) -> Sequence[PolicyORM]:
    # TODO raise IntegrityError if role is unknown and if possible via ORM
    if inherited:
        root_cte = (
            select(RoleORM.id.label("role_id"))
            .where(RoleORM.id == role)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM.parent_role_id).where(
                HierarchyORM.child_role_id == traversing_cte.c.role_id
            )
        )
        policy_orms = (
            db.scalars(
                select(PolicyORM).join(
                    relations_cte, PolicyORM.role_id == relations_cte.c.role_id
                )
            )
            .unique()
            .all()
        )
    else:
        policy_orms = (
            db.scalars(select(PolicyORM).where(PolicyORM.role_id == role))
            .unique()
            .all()
        )

    return policy_orms
