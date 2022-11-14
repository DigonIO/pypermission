# Testing

## Local testing (Arch Linux)

### MariaDB

```console
# mysql -u root -p
```

```sql
CREATE DATABASE pp_db;
CREATE USER 'pp_user'@'localhost' IDENTIFIED BY 'pp_pw';
GRANT ALL PRIVILEGES ON pp_db.* TO 'pp_user'@'localhost';
```
