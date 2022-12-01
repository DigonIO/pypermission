from typing import TypedDict

from pypermission import PermissionNode
from pypermission.serial import SerialAuthority


class BankAPIPermissionNode(PermissionNode):
    ACCOUNT_ = "account.*"  # grant full access to the account API
    ACCOUNT_CREATE = "account.create"
    ACCOUNT_GET_ = "account.get.*"
    ACCOUNT_GET_OWN = "account.get.own"
    ACCOUNT_LIST_ = "account.list.*"
    ACCOUNT_LIST_OWN = "account.list.own"
    ACCOUNT_DELETE = "account.delete"


# just a short form to avoid boiler plate code
NODE = BankAPIPermissionNode


class NoPermissionError(Exception):
    """Raised if the requesting user misses the required permission."""


# global variable to store the next account number
_next_account_number: int = 1


def get_next_account_number() -> int:
    global _next_account_number
    num = _next_account_number
    _next_account_number = num + 1
    return num


USER_ADMIN = "Georg Schmied"
USER_BANKER = "Johann Muller"
USER_CUSTOMER = "Heinrich Bauer"

GROUP_ADMIN = "role_admin"
GROUP_BANKER = "role_banker"
GROUP_CUSTOMER = "role_customer"


class Account:
    _number: int
    _username: str
    _balance: int

    def __init__(self, username: str) -> None:
        self._number = get_next_account_number()
        self._username = username
        self._balance = 0

    @property
    def number(self) -> int:
        return self._number

    @property
    def username(self) -> str:
        return self._username

    @property
    def balance(self) -> int:
        return self._balance

    def add_to_balance(self, diff: int) -> int:
        self._balance = self._balance + diff


class AccountResponse(TypedDict):
    number: int
    username: str
    balance: int


def response_factory(acc: Account) -> AccountResponse:
    return AccountResponse(number=acc.number, username=acc.username, balance=acc.balance)


class User:
    _username: str
    _auth = SerialAuthority
    _accounts: dict[int, Account]

    def __init__(self, username: str, auth: SerialAuthority) -> None:
        self._username = username
        self._auth = auth
        self._accounts = {}

        auth.add_subject(sid=username)

    @property
    def username(self) -> str:
        return self._username

    @property
    def accounts(self) -> dict[int, Account]:
        return self._accounts

    def has_permission(self, node: PermissionNode, payload: str | None = None) -> bool:
        self._auth.subject_inherits_permission(sid=self._username, node=node, payload=payload)

    def list_account_responses(self) -> list[AccountResponse]:
        return [response_factory(acc=acc) for num, acc in self._accounts]


class BankAPI:
    _auth: SerialAuthority
    _users: dict[str, User]
    _accounts: dict[int, Account]

    def __init__(self):
        self._auth = SerialAuthority(nodes=NODE)
        self._users = {}
        self._accounts = {}

    def account_create(self, username: int, owner_username: int) -> AccountResponse:
        user = self._users[username]

        if user.has_permission(node=NODE.ACCOUNT_CREATE):
            owner = self._users[owner_username]

            account = Account(username=owner.username)
            self._accounts[account.number] = account
            return response_factory(acc=account)

        raise NoPermissionError

    def account_get(self, username: int, account_number: int) -> AccountResponse:
        user = self._users[username]

        if account_number in user.accounts:
            if user.has_permission(node=NODE.ACCOUNT_GET_OWN):
                account = user.accounts[account_number]
                return response_factory(acc=account)

        if user.has_permission(node=NODE.ACCOUNT_GET_):
            account = self._accounts[account_number]
            return response_factory(acc=account)

        raise NoPermissionError

    def account_list(
        self, username: int, owner_username: int | None = None
    ) -> list[AccountResponse]:
        user = self._users[username]

        if owner_username is None:
            if user.has_permission(node=NODE.ACCOUNT_LIST_):
                return [response_factory(acc=acc) for _, acc in self._accounts]

            if user.has_permission(node=NODE.ACCOUNT_LIST_OWN):
                return user.list_account_responses()

        elif owner_username == username:
            if user.has_permission(node=NODE.ACCOUNT_LIST_OWN):
                return user.list_account_responses()

        else:  # owner_username == <other_username>
            if user.has_permission(node=NODE.ACCOUNT_LIST_):
                owner = self._users[owner_username]
                return owner.list_account_responses()

        raise NoPermissionError

    def account_delete(self, username: int, account_number: int) -> AccountResponse:
        user = self._users[username]

        if user.has_permission(node=NODE.ACCOUNT_DELETE):
            account = self._accounts.pop(account_number)
            return response_factory(acc=account)

        raise NoPermissionError

    def prepare_rbac_setup(self):
        self._auth.add_role(rid=GROUP_ADMIN)
        self._auth.add_role(rid=GROUP_BANKER)
        self._auth.add_role(rid=GROUP_CUSTOMER)

        self._auth.role_grant_permission(rid=GROUP_ADMIN, node=self._auth.root_node())

        self._auth.role_grant_permission(rid=GROUP_BANKER, node=NODE.ACCOUNT_CREATE)
        self._auth.role_grant_permission(rid=GROUP_BANKER, node=NODE.ACCOUNT_GET_)
        self._auth.role_grant_permission(rid=GROUP_BANKER, node=NODE.ACCOUNT_LIST_)
        self._auth.role_grant_permission(rid=GROUP_BANKER, node=NODE.ACCOUNT_DELETE)

        self._auth.role_grant_permission(rid=GROUP_CUSTOMER, node=NODE.ACCOUNT_GET_OWN)
        self._auth.role_grant_permission(rid=GROUP_CUSTOMER, node=NODE.ACCOUNT_LIST_OWN)

        user_admin = User(username=USER_ADMIN, auth=self._auth)
        user_banker = User(username=USER_BANKER, auth=self._auth)
        user_customer = User(username=USER_CUSTOMER, auth=self._auth)

        self._users[user_admin.username] = user_admin
        self._users[user_banker.username] = user_banker
        self._users[user_customer.username] = user_customer

        self._auth.role_assign_subject(rid=GROUP_ADMIN, sid=user_admin.username)
        self._auth.role_assign_subject(rid=GROUP_BANKER, sid=user_banker.username)
        self._auth.role_assign_subject(rid=GROUP_CUSTOMER, sid=user_customer.username)


bank_api = BankAPI()
