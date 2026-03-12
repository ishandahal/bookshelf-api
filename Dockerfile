FROM python:3.12-slim-bookworm

# Add uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1

WORKDIR /usr/local/app

# Copy project dependencies files only
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync

# Copy the project into the image
COPY . ./

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

CMD ["uv", "run", "uvicorn", "bookshelf_api.routes:app", "--host", "0.0.0.0", "--port", "8080"]
