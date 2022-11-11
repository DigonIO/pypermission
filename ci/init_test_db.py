import os
import sys
import mariadb

####################################################################################################
### Init MariaDB
####################################################################################################

MARIADB_ROOT_PASSWORD = os.environ.get("MARIADB_ROOT_PASSWORD")

try:
    conn = mariadb.connect(
        user="root", password=MARIADB_ROOT_PASSWORD, host="mariadb", port=3306, database="mysql"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()

cur.execute("CREATE DATABASE pp_db;")
cur.execute("CREATE USER 'pp_user'@'127.0.0.1' IDENTIFIED BY 'pp_pw';")
cur.execute("GRANT ALL PRIVILEGES ON pp_db.* TO 'pp_user'@'127.0.0.1';")
