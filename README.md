# RAISE Onboarding Portal Experience (ROPE)

ROPE aims to streamline the onboarding of RAISE adopters.

## Development

The repo includes a `docker` environment which can be launched as follows:

Set your GOOGLE_CLIENT_ID using the following command:

```bash
$ export GOOGLE_CLIENT_ID=<client_id>
```

```bash
$ docker compose up --build -d
```

Once running, the application components can be accessed at the following URLs:

* Frontend: [http://localhost:3000](http://localhost:3000)
* Backend API (docs): [http://localhost:3000/api/docs](http://localhost:3000/api/docs)

A user can be added to the database by running the following command: 
```bash
$ docker compose exec postgres psql -U pguser -d ropedb -c "INSERT INTO user_account (email, is_manager, is_admin, created_at, updated_at) VALUES ('user@email.com', false, true, now(), now());"
```

Devs can also test the deployment build of the frontend by running the following:

```bash
$ ROPE_APP_TARGET=deploy docker compose up --build -d
```

Code coverage reports can be generated when running tests:

```bash
$ pytest --cov=rope --cov-report=term --cov-report=html
```