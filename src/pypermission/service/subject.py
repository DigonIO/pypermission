from collections.abc import Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql import select

from pypermission.exc import PermissionNotGrantedError, PyPermissionError
from pypermission.models import (
    FrozenClass,
    HierarchyORM,
    MemberORM,
    Permission,
    Policy,
    PolicyORM,
    RoleORM,
    SubjectORM,
)
from pypermission.util.exception_handling import process_subject_role_integrity_error

################################################################################
#### SubjectService
################################################################################


class SubjectService(metaclass=FrozenClass):

    @classmethod
    def create(cls, *, subject: str, db: Session) -> None:
        """
        Create a new Subject.

        Parameters
        ----------
        subject : str
            The SubjectID of the Subject to create.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a Subject with the given SubjectID already exists or `subject` is empty string.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        try:
            subject_orm = SubjectORM(id=subject)
            db.add(subject_orm)
            db.flush()
        except IntegrityError:
            db.rollback()
            raise PyPermissionError(f"Subject '{subject}' already exists!")

    @classmethod
    def delete(cls, *, subject: str, db: Session) -> None:
        """
        Delete an existing Subject.

        Parameters
        ----------
        subject : str
            The SubjectID to delete.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If a Subject with the given SubjectID does not exist  or `subject` is empty string.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        subject_orm = db.get(SubjectORM, subject)
        if subject_orm is None:
            raise PyPermissionError(f"Subject '{subject}' does not exist!")
        db.delete(subject_orm)
        db.flush()

    @classmethod
    def list(cls, *, db: Session) -> tuple[str, ...]:
        """
        Get all Subjects.

        Parameters
        ----------
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all SubjectIDs.
        """
        subjects = db.scalars(select(SubjectORM.id)).all()
        return tuple(subjects)

    @classmethod
    def assign_role(cls, *, subject: str, role: str, db: Session) -> None:
        """
        Assign a Subject to a Role.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If `role` is empty string.
            If the Subject does not exist.
            If the Role does not exist.
            If the Subject was assigned to Role before. TODO
        """
        if role == "":
            raise PyPermissionError("Role name cannot be empty!")
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        try:
            member_orm = MemberORM(role_id=role, subject_id=subject)
            db.add(member_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            process_subject_role_integrity_error(err=err, subject=subject, role=role)

    @classmethod
    def deassign_role(cls, *, subject: str, role: str, db: Session) -> None:
        """
        Deassign a Subject from a Role.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        role : str
            The target RoleID.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If `role` is empty string.
            If the Subject does not exist.
            If the Role does not exist.
            If the Subject is not assigned to the Role. TODO
        """
        if role == "":
            raise PyPermissionError("Role name cannot be empty!")
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        # TODO raise IntegrityError if subject or role is unknown and if possible via ORM
        member_orm = db.get(MemberORM, (role, subject))
        if member_orm is None:
            subject_orm = db.get(SubjectORM, subject)
            if subject_orm is None:
                raise PyPermissionError(f"Subject '{subject}' does not exist!")
            role_orm = db.get(RoleORM, role)
            if role_orm is None:
                raise PyPermissionError(f"Role '{role}' does not exist!")
            raise PyPermissionError(
                f"Role '{role}' is not assigned to Subject '{subject}'!"
            )
        db.delete(member_orm)
        db.flush()

    @classmethod
    def roles(
        cls, *, subject: str, include_ascendant_roles: bool = False, db: Session
    ) -> tuple[str, ...]:
        """
        Get all Roles assigned to a Subject.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        include_ascendant_roles: bool
            Include all ascendant Roles.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all assigned RoleIDs.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If the target Subject does not exist.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        if include_ascendant_roles:
            root_cte = (
                select(MemberORM.role_id)
                .where(MemberORM.subject_id == subject)
                .cte(recursive=True)
            )
            traversing_cte = root_cte.alias()
            relations_cte = root_cte.union_all(
                select(HierarchyORM.parent_role_id).join(
                    traversing_cte,
                    HierarchyORM.child_role_id == traversing_cte.c.role_id,
                )
            )
            selection = select(relations_cte)
            roles = db.scalars(selection).unique().all()
        else:
            roles = db.scalars(
                select(MemberORM.role_id).where(MemberORM.subject_id == subject)
            ).all()

        if len(roles) == 0 and db.get(SubjectORM, subject) is None:
            raise PyPermissionError(f"Subject '{subject}' does not exist!")
        return tuple(roles)

    @classmethod
    def check_permission(
        cls,
        *,
        subject: str,
        permission: Permission,
        db: Session,
    ) -> bool:
        """
        Check if a Subject has access to a specific Permission via its Role hierarchy.

        Parameters
        ----------
        subject : str
            The target SubjectID.
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
            If `subject` is empty string.
            If the target Subject does not exist. TODO
        """
        # TODO raise IntegrityError if subject is unknown and if possible via ORM
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        root_cte = (
            select(MemberORM.role_id)
            .where(MemberORM.subject_id == subject)
            .cte(recursive=True)
        )

        traversing_cte = root_cte.alias()
        relations_cte = root_cte.union_all(
            select(HierarchyORM.parent_role_id).join(
                traversing_cte, HierarchyORM.child_role_id == traversing_cte.c.role_id
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
        if len(policy_orms) > 0:
            return True
        subject_orm = db.get(SubjectORM, subject)
        if subject_orm is None:
            raise PyPermissionError(f"Subject '{subject}' does not exist!")
        return False

    @classmethod
    def assert_permission(
        cls,
        *,
        subject: str,
        permission: Permission,
        db: Session,
    ) -> None:
        """
        Asserts that a Subject has access to a specific Permission via its Role hierarchy.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        permission : Permission
            The Permission to check for.
        db : Session
            The SQLAlchemy session.

        Raises
        ------
        PyPermissionNotGrantedError
            If the Permission is not granted.
        PyPermissionError
            If `subject` is empty string.
            If the target Subject does not exist.
        """
        if not cls.check_permission(subject=subject, permission=permission, db=db):
            raise PermissionNotGrantedError(
                f"Permission '{permission}' is not granted for Subject '{subject}'!"
            )

    @classmethod
    def permissions(cls, *, subject: str, db: Session) -> tuple[Permission, ...]:
        """
        Get all Permissions a Subject has access to via its Role hierarchy.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[Permission, ...]
            A tuple containing all granted Permissions.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If the target Subject does not exist.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        policy_orms = _get_policy_orms_for_subject(subject=subject, db=db)

        return tuple(
            Permission(
                resource_type=policy_orm.resource_type,
                resource_id=policy_orm.resource_id,
                action=policy_orm.action,
            )
            for policy_orm in policy_orms
        )

    @classmethod
    def policies(cls, *, subject: str, db: Session) -> tuple[Policy, ...]:
        """
        Get all Policies associated to a Subject via its Role hierarchy.

        Parameters
        ----------
        subject : str
            The target SubjectID.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[Policies, ...]
            A tuple containing all granted Policies.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If the target Subject does not exist.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        policy_orms = _get_policy_orms_for_subject(subject=subject, db=db)

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
        subject: str,
        resource_type: str,
        resource_id: str,
        inherited: bool = True,
        db: Session,
    ) -> tuple[str, ...]:
        """
        Get all Actions granted to a **Subject** on a specific **Resource**.

        Parameters
        ----------
        subject : str
            The target **SubjectID**.
        resource_type : str
            The **ResourceType** of the **Resource**.
        resource_id : str
            The **ResourceID** of the **Resource**.
        inherited : bool
            Whether to include inherited **Actions** from **Role** hierarchies.
        db : Session
            The SQLAlchemy session.

        Returns
        -------
        tuple[str, ...]
            A tuple containing all granted **Action** values.

        Raises
        ------
        PyPermissionError
            If `subject` is empty string.
            If `resource_type` is empty string.
            If the target **Subject** does not exist.
        """
        if subject == "":
            raise PyPermissionError("Subject name cannot be empty!")
        if resource_type == "":
            raise PyPermissionError("Resource type cannot be empty!")
        if inherited:
            root_cte = (
                select(MemberORM.role_id)
                .where(MemberORM.subject_id == subject)
                .cte(recursive=True)
            )
            traversing_cte = root_cte.alias()
            relations_cte = root_cte.union_all(
                select(HierarchyORM.parent_role_id).join(
                    traversing_cte,
                    HierarchyORM.child_role_id == traversing_cte.c.role_id,
                )
            )
            actions = (
                db.scalars(
                    select(PolicyORM.action, PolicyORM.role_id)
                    .join(relations_cte, PolicyORM.role_id == relations_cte.c.role_id)
                    .where(
                        PolicyORM.resource_type == resource_type,
                        PolicyORM.resource_id.in_((resource_id, "*")),
                    )
                )
                .unique()
                .all()
            )
            tuple(actions)
        else:
            selection = (
                select(PolicyORM.action, PolicyORM.role_id)
                .join(MemberORM, MemberORM.role_id == PolicyORM.role_id)
                .where(
                    MemberORM.subject_id == subject,
                    PolicyORM.resource_type == resource_type,
                    PolicyORM.resource_id.in_((resource_id, "*")),
                )
            )
            actions = db.scalars(selection).unique().all()
        if len(actions) == 0 and db.get(SubjectORM, subject) is None:
            raise PyPermissionError(f"Subject '{subject}' does not exist!")
        return tuple(actions)


################################################################################
#### Util
################################################################################


def _get_policy_orms_for_subject(*, subject: str, db: Session) -> Sequence[PolicyORM]:
    """
    Get all PolicyORM objects associated to a Subject via its Role hierarchy.

    Parameters
    ----------
    subject : str
        The target SubjectID.
    db : Session
        The SQLAlchemy session.

    Returns
    -------
    Sequence[PolicyORM]
        A Sequence containing all associated PolicyORM objects.

    Raises
    ------
    PyPermissionError
        If the target Subject does not exist.
    """
    subject_orm = db.get(SubjectORM, subject)
    if not subject_orm:
        raise PyPermissionError(f"Subject '{subject}' does not exist!")
    root_cte = (
        select(MemberORM.role_id)
        .where(MemberORM.subject_id == subject)
        .cte(recursive=True)
    )

    traversing_cte = root_cte.alias()
    relations_cte = root_cte.union_all(
        select(HierarchyORM.parent_role_id).join(
            traversing_cte, HierarchyORM.child_role_id == traversing_cte.c.role_id
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

    return policy_orms
