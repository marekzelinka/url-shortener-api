# URL shortener RESTful API

A fast, fully async and reliable **URL shortener RESTful API** built with **Python** and **FastAPI** framework. It uses **MongoDB** for storing shortened URLs data and implements user registration via **OAuth2 JWT authentication**.

## Features

- Dockerized and ready to be deployed.
- Fully async and non-blocking.
- Uses **FastAPI** framework for API development.
- CORS (Cross Origin Resource Sharing) support.
- Uses **MongoDB** as data store for users and shortened URLs.
- **OAuth2** (with hashed passwords and JWT tokens) based user authentication.
- Extensible architecture for adding new API endpoints and services.
- Uses **UV** for dependency management.
- Automated code formatting, linting and type-checking using **Ruff** and **Pyrefly**.
- Pagination support for listing shortened URLs and users.
- **Fully type annotated** code for better IDE support and code quality.

## Tech stack

- [FastAPI](https://fastapi.tiangolo.com/) - web framework
- [Beanie](https://beanie-odm.dev/) - MongoDB ODM for Python
- [MongoDB](https://sqlite.org/) - no-sql database
- [uv](https://docs.astral.sh/uv/) - project manager, and much more...
- [Ruff](https://docs.astral.sh/ruff/) - linter and formatter
- [Pyrefly](https://pyrefly.org/) - type checker
- [just](https://just.systems/) - command runner

## Setup

### Prep

This project uses the modern `pyproject.toml` standard for dependency management and requires the `uv` tool to manage the environment.

**Ensure `uv` is installed** globally on your system. If not, follow the official installation guide for [`uv`](https://docs.astral.sh/uv/).

Create a [MongoDB Atlas](https://www.mongodb.com/docs/atlas/tutorial/create-atlas-account/) for cloud-based MongoDB.

### Install

1.  **Setup venv and install dependencies:**

    ```sh
    uv sync
    ```

2.  **Set up Environment Variables:**

    Copy the contents of [`.env.example`](./.env.example) to `.env` file in the root directory.
    
     ```sh
    cp .env.example .env
    ```

### Running the application

Start the development server using `uv`:

```sh
uv run uvicorn app.main:app --reload
```

Once started, access the interactive docs at: [http://localhost:8000/docs](http://localhost:8000/docs).

### Local dev

1. Setup your editor to work with [ruff](https://docs.astral.sh/ruff/editors/setup/) and [Pyrefly](https://pyrefly.org/en/docs/IDE/).

2. *Optional* Install the [justfile extension](https://just.systems/man/en/editor-support.html) for your editor, and use the provided `./justfile` to run commands.

## Code Quality

- Check for linting errors using `ruff check`: 

  ```sh
  uv run ruff check --fix
  ```

- Format the code using `ruff format`: 

  ```sh
  uv run ruff format
  ```

- Run typechecker using `ty check`: 

  ```sh
  uv run pyrefly check
  ```

## TODO

- [ ] deploy to Fly.io
- [ ] add admin routes for managment
- [ ] private short urls (add `is_public` field to `ShortURL`)
