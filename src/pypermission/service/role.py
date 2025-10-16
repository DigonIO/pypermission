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
from pypermission.exc import PyPermissionError, PyPermissionNotGrantedError

################################################################################
#### RoleService
################################################################################


class RoleService(metaclass=FrozenClass):

    @classmethod
    def create(cls, *, role: str, db: Session) -> None:
        """
        Create a new Role.

        Parameters
        ----------
        role : str
            The RoleID of the Role to create.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a Role with the given RoleID already exists.
        """
        try:
            role_orm = RoleORM(id=role)
            db.add(role_orm)
            db.flush()
        except IntegrityError:
            db.rollback()
            raise PyPermissionError(f"Role '{role}' already exists!")

    @classmethod
    def delete(cls, *, role: str, db: Session) -> None:
        """
        Delete an existing Role.

        Parameters
        ----------
        role : str
            The RoleID to delete.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a Role with the given RoleID does not exist.
        """
        role_orm = db.get(RoleORM, role)
        if role_orm is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        db.delete(role_orm)
        db.flush()

    @classmethod
    def list(cls, *, db: Session) -> tuple[str, ...]:
        """
        Get all Roles.

        Parameters
        ----------
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all RoleIDs.
        """
        role_orms = db.scalars(select(RoleORM)).all()
        return tuple(role_orm.id for role_orm in role_orms)

    @classmethod
    def add_hierarchy(cls, *, parent_role: str, child_role: str, db: Session) -> None:
        """
        Add a parent-child hierarchy between two Roles.

        Parameters
        ----------
        parent_role : str
            The parent RoleID.
        child_role : str
            The child RoleID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If arguments `parent_role` and `child_role` are equal.
            If one or both Roles do not exist.
            If adding the hierarchy would create a cycle.
            If the hierarchy already exists.
        """
        if parent_role == child_role:
            raise PyPermissionError(f"RoleIDs must not be equal: '{parent_role}'!")

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
            raise PyPermissionError("Desired hierarchy would create a cycle!")

        try:
            hierarchy_orm = HierarchyORM(
                parent_role_id=parent_role, child_role_id=child_role
            )
            db.add(hierarchy_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            raise PyPermissionError(
                f"Hierarchy '{parent_role}' -> '{child_role}' exists!"
            )

    @classmethod
    def remove_hierarchy(
        cls, *, parent_role: str, child_role: str, db: Session
    ) -> None:
        """
        Remove a parent-child hierarchy between two Roles.

        Parameters
        ----------
        parent_role : str
            The parent RoleID.
        child_role : str
            The child RoleID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If arguments `parent_role` and `child_role` are equal.
            If one or both Roles do not exist.
            If the hierarchy does not exist.
        """
        if parent_role == child_role:
            raise PyPermissionError(f"RoleIDs must not be equal: '{parent_role}'!")

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
                    f"Hierarchy '{parent_role}' -> '{child_role}' does not exist!"
                )

        db.delete(hierarchy_orm)
        db.flush()

    @classmethod
    def parents(cls, *, role: str, db: Session) -> tuple[str, ...]:
        """
        Get all parent Roles.

        Parameters
        ----------
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all parent RoleIDs.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
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
        """
        Get all child Roles.

        Parameters
        ----------
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all child RoleIDs.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
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
        """
        Get all ancestor Roles.

        Parameters
        ----------
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all ancestor RoleIDs.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
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
        """
        Get all descending Roles.

        Parameters
        ----------
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all descending RoleIDs.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
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
    def subjects(
        cls, *, role: str, include_descendant_subjects: bool = False, db: Session
    ) -> tuple[str, ...]:
        """
        Get all Subjects assigned to a Role.

        Parameters
        ----------
        role : str
            The target RoleID.
        include_descendant_subjects: bool
            Include all Subjects for descendant Roles.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all assigned SubjectIDs.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
        if include_descendant_subjects:
            root_cte = (
                select(RoleORM.id.label("role_id"))
                .where(RoleORM.id == role)
                .cte(recursive=True)
            )

            traversing_cte = root_cte.alias()
            relations_cte = root_cte.union_all(
                select(HierarchyORM.child_role_id).where(
                    HierarchyORM.parent_role_id == traversing_cte.c.role_id
                )
            )
            subjects = (
                db.scalars(
                    select(MemberORM.subject_id).join(
                        relations_cte, MemberORM.role_id == relations_cte.c.role_id
                    )
                )
                .unique()
                .all()
            )
        else:
            subjects = db.scalars(
                select(MemberORM.subject_id).where(MemberORM.role_id == role)
            ).all()

        if len(subjects) == 0 and db.get(RoleORM, role) is None:
            raise PyPermissionError(f"Role '{role}' does not exist!")
        return tuple(subjects)

    @classmethod
    def grant_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        """
        Grant a Permission to a Role.

        Parameters
        ----------
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
            If the Permission was granted before. TODO
        """
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
            # TODO check the error cause
            raise PyPermissionError(f"Role '{role}' does not exist!")

    @classmethod
    def revoke_permission(
        cls,
        *,
        role: str,
        permission: Permission,
        db: Session,
    ) -> None:
        """
        Revoke a Permission from a Role.

        Parameters
        ----------
        role : str
            The target Role ID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
            If the Permission was not granted before. TODO
        """
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
            # TODO check the error cause
            raise PyPermissionError(f"Role '{role}' does not exist!")

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
        """
        Check if a Role has a Permission.

        Parameters
        ----------
        role : str
            The target RoleID.
        permission : Permission
            The Permission to check for.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        bool
            True if the Permission is granted.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist. TODO
        """
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
        """
        Check if a Role has a Permission.

        Parameters
        ----------
        role : str
            The target RoleID.
        permission : Permission
            The Permission to check for.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionNotGrantedError
            If the Permission is not granted.
        PyPermissionError
            If the target Role does not exist.
        """
        if not cls.check_permission(role=role, permission=permission, db=db):
            raise PyPermissionNotGrantedError(
                f"Permission '{permission}' is not granted for Role '{role}'!"
            )

    @classmethod
    def permissions(
        cls,
        *,
        role: str,
        inherited: bool = True,
        db: Session,
    ) -> tuple[Permission, ...]:
        """
        Get all granted Permissions for a Role.

        Parameters
        ----------
        role : str
            The target RoleID.
        inherited : bool
            Includes all Permissions inherited by ancestor Roles.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[Permission, ...]
            A tuple containing all granted Permissions.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
        policy_orms = _get_policy_orms_for_role(role=role, inherited=inherited, db=db)

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
        """
        Get all granted Policies for a Role.

        Parameters
        ----------
        role : str
            The target RoleID.
        inherited : bool
            Includes all Policies inherited by ancestor Roles.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[Policies, ...]
            A tuple containing all granted Policies.

        Raises
        ------
        PyPermissionError
            If the target Role does not exist.
        """
        policy_orms = _get_policy_orms_for_role(role=role, inherited=inherited, db=db)

        return tuple(
            Policy(
                role=policy_orm.role_id,
                permission=Permission(
                    resource_type=policy_orm.resource_type,
                    resource_id=policy_orm.resource_id,
                    action=policy_orm.action,
                ),
            )
            for policy_orm in policy_orms
        )

    @classmethod
    def actions_on_resource(
        cls,
        *,
        role: str,
        resource_type: str,
        resource_id: str,
        inherited: bool = True,
        db: Session,
    ) -> tuple[str, ...]:
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
            selection = (
                select(PolicyORM.action)
                .join(
                    relations_cte,
                    PolicyORM.role_id == relations_cte.c.role_id,
                )
                .where(
                    PolicyORM.resource_type == resource_type,
                    PolicyORM.resource_id.in_((resource_id, "*")),
                )
            )
        else:
            selection = select(PolicyORM.action).where(
                PolicyORM.role_id == role,
                PolicyORM.resource_type == resource_type,
                PolicyORM.resource_id.in_((resource_id, "*")),
            )
        result = db.scalars(selection).all()
        return tuple(result)


################################################################################
#### Util
################################################################################


def _get_policy_orms_for_role(
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
