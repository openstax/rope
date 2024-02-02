# RAISE Onboarding Portal Experience (ROPE)

ROPE aims to streamline the onboarding of RAISE adopters.

## Development

The repo includes a `docker` environment which can be launched as follows:

```bash
$ docker compose up --build -d
```

Once running, the application components can be accessed at the following URLs:

* Frontend: [http://localhost:3000](http://localhost:3000)
* Backend API (docs): [http://localhost:3000/api/docs](http://localhost:3000/api/docs)

Devs can also test the deployment build of the frontend by running the following:

```bash
$ ROPE_APP_TARGET=deploy docker compose up --build -d
```

Code coverage reports can be generated when running tests:

```bash
$ pytest --cov=rope --cov-report=term --cov-report=html
```