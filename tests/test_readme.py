import pathlib

path = pathlib.Path(__file__).parent.absolute()


def test_readme_code_example():

    from pypermission import PermissionNode
    from pypermission.serial import SerialAuthority

    class Nodes(PermissionNode):
        CHAT_ = "chat.*"  # parent
        CHAT_GLOBAL = "chat.global"  # leaf
        CHAT_MODERATOR = "chat.moderator"  # leaf
        TICKET_ = "ticket.*"  # parent
        TICKET_OPEN = "ticket.open"  # leaf
        TICKET_CLOSE_ = "ticket.close.*"  # parent
        TICKET_CLOSE_OWN = "ticket.close.own"  # leaf
        TICKET_CLOSE_ALL = "ticket.close.all"  # leaf
        TICKET_ASSIGN = "ticket.assign"  # leaf

    auth = SerialAuthority(nodes=Nodes)

    auth.load_file(path=path / "test_readme.yaml")

    assert auth.subject_has_permission(sid="Bob", node=Nodes.CHAT_GLOBAL)
    assert auth.subject_has_permission(sid="Alice", node=Nodes.CHAT_MODERATOR)
    assert auth.subject_has_permission(sid="Bob", node=Nodes.TICKET_OPEN)
    assert auth.subject_has_permission(sid="Alice", node=Nodes.TICKET_CLOSE_ALL)
