# Alembic Migration

## Introduction
Alembic is a database migration tool for the SQLAlchemy. This documentation outlines the steps to use Alembic for creating migrations, downgrading migrations and deleting version files. 



## Autogenerate migrations

```bash
alembic revision --autogenerate -m "Migration description"
```

To have these changes reflect in your database you run the following command.

```bash
alembic upgrade head
```


## Downgrading migrations

Lets say the developer made a mistake and would like to downgrade the migration. 
They can create a downgrade migration.

```bash
alembic revision --downgrade <target_revision>
```
You may make changes to the downgrade versions file's `downgrade` method to update the databsae. 

To have these changes reflect in your database you run the following command.

```bash
alembic downgrade -1
```

## Deleting a version file

Deleting a migration file does not automatically reverse the changes it introduced in the database. If the developer wants to delete the most recent version file they may have created accidentally locally.
Assuming `alembic upgrade head` has already been run.

Run the following command
```bash 
alembic downgrade -1 
```
By using `alembic downgrade -1` before deleting the version file, you ensure that the changes introduced by the last migration are properly rolled back in the database. If you do not downgrade before deleting a version file your database may be corrupted 