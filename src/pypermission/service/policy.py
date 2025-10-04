from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from pypermission.models import Policy, PolicyORM, FrozenClass
from pypermission.exc import PyPermissionError

################################################################################
#### PolicyService
################################################################################


class PolicyService(metaclass=FrozenClass):

    @classmethod
    def create(
        cls,
        *,
        policy: Policy,
        db: Session,
    ) -> None:
        try:
            policy_orm = PolicyORM(
                role_id=policy.role,
                resource_type=policy.permission.resource_type,
                resource_id=policy.permission.resource_id,
                action=policy.permission.action,
            )
            db.add(policy_orm)
            db.flush()
        except IntegrityError as err:
            db.rollback()
            # TODO 'psycopg.errors.UniqueViolation'

    @classmethod
    def delete(
        cls,
        *,
        policy: Policy,
        db: Session,
    ) -> None:
        policy_tuple = (
            policy.role,
            policy.permission.resource_type,
            policy.permission.resource_id,
            policy.permission.action,
        )
        policy_orm = db.get(
            PolicyORM,
            policy_tuple,
        )
        if policy_orm is None:
            raise PyPermissionError(f"Unknown policy '{policy_tuple}'!")

        db.delete(policy_orm)
        db.flush()
