import datetime as dt
import os
import sys
import time

import mariadb
from scheduler import Scheduler

####################################################################################################
### Init MariaDB
####################################################################################################

MARIADB_ROOT_PASSWORD = os.environ.get("MARIADB_ROOT_PASSWORD")


def init_mariadb():
    try:
        conn = mariadb.connect(
            user="root", password=MARIADB_ROOT_PASSWORD, host="mariadb", port=3306, database="mysql"
        )

        cur = conn.cursor()
        cur.execute("CREATE DATABASE pp_db;")
        cur.execute("CREATE USER 'pp_user'@'%' IDENTIFIED BY 'pp_pw';")
        cur.execute("GRANT ALL PRIVILEGES ON pp_db.* TO 'pp_user'@'%';")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return False
    return True


####################################################################################################
### Init PostgreSQL
####################################################################################################


def init_postgresql():  # TODO
    return True


####################################################################################################
### Init MySQL
####################################################################################################


def init_mysql():  # TODO
    return True


####################################################################################################
### Init all
####################################################################################################


def init(dbs: dict):
    for key, value in dbs.items():
        if value["init"] is False:
            value["init"] = value["handle"]()


def main():
    scheduler = Scheduler()

    dbs = {
        "mariadb": {"init": False, "handle": init_mariadb},
        "postgresql": {"init": False, "handle": init_postgresql},
        "mysql": {"init": False, "handle": init_mysql},
    }

    scheduler.cyclic(dt.timedelta(seconds=1), init, kwargs={"dbs": dbs}, max_attempts=10)

    while scheduler.jobs:
        scheduler.exec_jobs()
        time.sleep(0.1)

    for _, value in dbs.items():
        if value["init"] is False:
            sys.exit(1)


if __name__ == "__main__":
    main()
