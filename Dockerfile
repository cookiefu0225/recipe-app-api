FROM python:3.9-alpine3.13
LABEL maintainer="frankyang6668@gmail.com"

# Made output show directly on the console
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app
WORKDIR /app
EXPOSE 8000


ARG DEV=false
    # Avoid python dependencies confliction
RUN python -m venv /py && \    
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        # These will be removed after running because we just require it and are not going to use it.
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Keep Docker images as lightweight as possible (don't want extra dependencies)
    # Saves spaces and speed
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Not to use the root user
    # Not recommended to run the applications using the root user
    # If app got compromised, the attacker can get full access 
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Update environment variable
ENV PATH="/py/bin:$PATH"

# Should be last line, switch to the user
# Protect root privileges
USER django-user