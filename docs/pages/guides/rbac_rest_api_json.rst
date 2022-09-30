
==================
RBAC for REST APIs
==================

In diesem Guide lernen wir wie man "role based access control" (RBAC) mit Hilfe von
PyPermission implementieren kann.
Dazu verwenden wir Authority die JSON für die Persistenz verwendet.
Alternativ kann auch die Authority verwendet werden die YAML verwendet, denn ihre API ist die Selbe.


Um den Guide anschaulich zu gestalten entwickeln wir einen naiven Dummy für die REST API einer Bank.
Dabei beschränken wir uns auf den Teil der API, der sich um die Bankkontoverwaltung kümmert.
Wir nehmen weiter an, dass es drei Nutzerarten für die API gibt, Admins, Bänker und Kunden.
Aufgrund dieser Gruppenstruktur entscheiden wir uns dazu RBAC zu implementiert.









Zunächst importieren wir alle nötigen Objekte aus den entsprechenden Modulen.

.. code-block:: python

    from typing import TypedDict
    from pypermission.json import Authority, PermissionNode

Nun definieren wir die möglichen Berechtigungen, die in der Bankkontoverwaltungs API relevant sind.
Hierzu definieren wir eine Klasse indem wir von der PermissionNode Klasse erben.
Die einzelnen permission nodes werden wie enum Werte angelegt.
Hier ist zu beachten, dass ein User der eine parent permission node hat, ebenfalls alle
child permissions hat.
Am Ende definieren wir noch eine Exception für die Bank API, die raised wird, falls ein User
nicht die Rechte für einen gewünschten request hat.

In order to define the relevant permissions of a Accountmanagement API we define a class
by inheriting from the PermissionNode class.
The permission nodes are implemented as enum values.
Keep in mind, that a user with a parent permission node also has all child permissions.
Additionally we define a exception which is raised if a user does not have the needed permission
for his request.




.. code-block:: python

    class BankAPIPermissionNode(PermissionNode):
        ACCOUNT_ = "account.*"  # parent
        ACCOUNT_CREATE = "account.create"  # leaf
        ACCOUNT_GET_ = "account.get.*"  # parent
        ACCOUNT_GET_OWN = "account.get.own"  # leaf
        ACCOUNT_LIST_ = "account.list.*"  # parent
        ACCOUNT_LIST_OWN = "account.list.own"  # leaf
        ACCOUNT_DELETE = "account.delete"  # leaf


    # just a short handle to avoid boilerplate code
    NODE = BankAPIPermissionNode

    class NoPermissionError(Exception):
    """Raised if the requesting user misses the required permission."""

Wir benötigen eine Möglichkeit um Kontonummern zu generieren.
Dazu schreiben wir uns eine kleine Helferfunktion.

In order to generate Account numbers we define a helper function: 

.. code-block:: python

    # global variable to store the next account number
    _next_account_number: int = 1


    def gen_acc_num() -> int:
        """Generate a new account number."""
        global _next_account_number
        num = _next_account_number
        _next_account_number = num + 1
        return num

In unserm Beispiel soll es User und Usergruppen geben.
Dazu benötigen wir Usernamen und IDs um die Gruppen zu identifizieren.
Diese Werte definieren wir nun global.



.. code-block:: python

    USER_ADMIN = "Georg Schmied"
    USER_BANKER = "Johann Muller"
    USER_CUSTOMER = "Heinrich Bauer"

    GROUP_ADMIN = "group_admin"
    GROUP_BANKER = "group_banker"
    GROUP_CUSTOMER = "group_customer"

Ein Bankkonto wird intern in der Bank API als Klasse repräsentiert.
Da solche Klassen typischerweise mehr Informationen beinhaltet als man über die REST API versenden
möchte, definieren wir noch beispielhaft ein Response Objekte.

Internally, a bank account is represented as a class.
Usually classes contain more information than those one wants to send via the REST API,
therefore we define a response object.

.. code-block:: python

    class Account:
        _number: int
        _username: str
        _balance: int

        def __init__(self, username: str) -> None:
            self._number = gen_acc_num()
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


    class AccountResponse(TypedDict):
        number: int
        username: str
        balance: int


    def response_factory(acc: Account) -> AccountResponse:
        return AccountResponse(number=acc.number, username=acc.username, balance=acc.balance)

Genau wie für das Konto, so definieren wir klasse für den User.
Die Userklasse erleichtert uns die Zuordnung von User und Bankkonto.
Zusätzlich weist der User eine Methode auf, mit welcher man einfach die Berechtigungen des Users
überprüfen kann.

The user class is build resembling the bank account class.
It facilitates the assignment of the user to his bank account.
Furthermore the user class contains a method which lists all permissions of a user.


.. code-block:: python

    class User:
        _username: str
        _auth = Authority
        _accounts: dict[int, Account]

        def __init__(self, username: str, auth: Authority) -> None:
            self._username = username
            self._auth = auth
            self._accounts = {}

            auth.add_subject(s_id=username)

        @property
        def username(self) -> str:
            return self._username

        @property
        def accounts(self) -> dict[int, Account]:
            return self._accounts

        def has_permission(self, node: PermissionNode, payload: str | None = None) -> bool:
            self._auth.subject_has_permission(s_id=self._username, node=node, payload=payload)

        def list_account_responses(self) -> list[AccountResponse]:
            return [response_factory(acc=acc) for num, acc in self._accounts]

Die letzte Klasse die wir in diese Guide definieren ist der Dummy für die REST API der Bank.
Mit Dieser ist es möglich Bankkonten zu erzeugen, einzeln oder als List abzufragen
und zu löschen.
Damit nicht jeder User Zugriff auf alle Funktion der API hat wird hier RBAC
implementiert.
Letztlich muss man überlegen welche Kombination an Argumenten an die API
übergeben wird.
Anhand dieser Kombination lässt sich entscheiden, welche Funktion eines Endpunktes der User
verwenden möchte.
Im Anschluss wird geprüft ob der User die Berechtigung zu dieser Funktion hat.
Dazu besitzt die Bank API eine Instanz der Authority welche als zentrale Anlaufstelle für alle
permission relevanten Prozesse fungiert.
Die Methode ``BankAPI.prepare_rbac_setup`` ist in diesem Beispiel gedacht, den State der API
zu inizieren.
Die dort simulierte Businesslogik für in einem realen Fall, in anderen Teilen der Bank API
umgesetzt werden.




.. code-block:: python

    class BankAPI:
        _auth: Authority
        _users: dict[str, User]
        _accounts: dict[int, Account]

        def __init__(self):
            self._auth = Authority(nodes=NODE)  # register permission nodes
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
            self._auth.add_group(g_id=GROUP_ADMIN)
            self._auth.add_group(g_id=GROUP_BANKER)
            self._auth.add_group(g_id=GROUP_CUSTOMER)

            self._auth.group_add_permission(g_id=GROUP_ADMIN, node=self._auth.root_node())

            self._auth.group_add_permission(g_id=GROUP_BANKER, node=NODE.ACCOUNT_CREATE)
            self._auth.group_add_permission(g_id=GROUP_BANKER, node=NODE.ACCOUNT_GET_)
            self._auth.group_add_permission(g_id=GROUP_BANKER, node=NODE.ACCOUNT_LIST_)
            self._auth.group_add_permission(g_id=GROUP_BANKER, node=NODE.ACCOUNT_DELETE)

            self._auth.group_add_permission(g_id=GROUP_CUSTOMER, node=NODE.ACCOUNT_GET_OWN)
            self._auth.group_add_permission(g_id=GROUP_CUSTOMER, node=NODE.ACCOUNT_LIST_OWN)

            user_admin = User(username=USER_ADMIN, auth=self._auth)
            user_banker = User(username=USER_BANKER, auth=self._auth)
            user_customer = User(username=USER_CUSTOMER, auth=self._auth)

            self._users[user_admin.username] = user_admin
            self._users[user_banker.username] = user_banker
            self._users[user_customer.username] = user_customer

            self._auth.group_add_subject(g_id=GROUP_ADMIN, s_id=user_admin.username)
            self._auth.group_add_subject(g_id=GROUP_BANKER, s_id=user_banker.username)
            self._auth.group_add_subject(g_id=GROUP_CUSTOMER, s_id=user_customer.username)
