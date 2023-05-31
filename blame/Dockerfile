FROM alpine:3 as builder

RUN apk add gcc musl-dev

WORKDIR /build
ADD readflag.c .
RUN gcc -o readflag -static readflag.c

FROM alpine:3

RUN apk add python3 py3-pip git && \
    python3 -m pip install pipenv

COPY --from=builder --chown=root:root /build/readflag /readflag
COPY --chown=root:root flag /flag
RUN chmod +s /readflag && \
    chmod 400 /flag

WORKDIR /app
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONFAULTHANDLER=1 PYTHONUNBUFFERED=1

COPY Pipfile* /app/
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

COPY . /app/

USER 1000
CMD ["pipenv", "run", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
