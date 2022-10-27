# Testing

## Local testing (Arch Linux)

### MariaDB

```console
# mysql -u root -p
```

```sql
CREATE DATABASE pp_test;
CREATE USER 'pp_test'@'localhost' IDENTIFIED BY 'pp_test';
GRANT ALL PRIVILEGES ON pp_test.* TO 'pp_test'@'localhost';
```
