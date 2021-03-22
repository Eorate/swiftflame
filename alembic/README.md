Generic single-database configuration.

```
# To create a migration script in /versions folder
$ alembic revision -m "<Insert database change description here>" 
# To apply the latest changes
$ alembic upgrade head
# To apply changes for a single revision
$ alembic upgrade <revision_id>
# To go back to the previous database state
$ alembic downgrade -1
# To revert to the very first change
$ alembic downgrade base
```

We are running alembic migrations every time we do a deploy. This means that we
have to be careful not to introduce code that relies on non-existing database
changes.

The approach we have decided to take is
1. Create a migration script to introduce the new database changes. Deploy.
2. Introduce the new changes in code. But keep the old stuff. Deploy.
3. If the changes are good, remove the old stuff from code. Deploy.
4. Create a migration script to remove the old database changes. Deploy.

