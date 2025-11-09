from sqlalchemy.orm import Session

from pypermission.service.role import RoleService as RS
from pypermission.service.subject import SubjectService as SS
from pypermission.models import Permission
from pypermission.util.role import role_dag
from pypermission.util.plot import plot_factory

################################################################################
#### Test util plot_factory
################################################################################


def test_plot_factory_execution__success(db: Session) -> None:
    RS.create(role="mod", db=db)
    RS.create(role="admin", db=db)

    SS.create(subject="Alex", db=db)
    SS.create(subject="Max", db=db)

    RS.create(role="user[Alex]", db=db)
    RS.create(role="user[Max]", db=db)

    SS.assign_role(subject="Alex", role="admin", db=db)
    SS.assign_role(subject="Alex", role="user[Alex]", db=db)
    SS.assign_role(subject="Max", role="mod", db=db)
    SS.assign_role(subject="Max", role="user[Max]", db=db)

    view_all = Permission(resource_type="user", resource_id="*", action="view")
    edit_all = Permission(resource_type="user", resource_id="*", action="edit")

    RS.grant_permission(role="mod", permission=view_all, db=db)
    RS.grant_permission(role="admin", permission=edit_all, db=db)

    dag = role_dag(db=db)
    plot_factory(dag=dag)
