FROM python:3.7-slim AS active-server

RUN mkdir /local

WORKDIR /local

# Add code
COPY ./app/ /local/app/

# Django
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install \
      --no-install-recommends --no-install-suggests -y \
      gettext \
      gcc \
      libc6-dev \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y \
    && apt-get clean \
    && addgroup --gid 4000 apprunner \
    && adduser --system --disabled-password --disabled-login --gecos "" --gid 4000 --uid 4000 apprunner \
    && chown -R apprunner:apprunner /local \
    && chsh -s /bin/false apprunner

# Install PIP requirements
COPY --chown=apprunner:apprunner ./config/ /local/config/

ARG REQS_FILE

RUN pip install --upgrade pip  \
    && pip install --extra-index-url https://pypi-6etexgwgpa-ew.a.run.app/simple/ -r /local/config/${REQS_FILE:-"deploy.txt"}

# Copy application code
COPY --chown=apprunner:apprunner ./app/ /local/app/

WORKDIR /local/app

# Compile translations
# Uncomment when locale folder is created and makemessages command is executed
# RUN django-admin compilemessages

USER apprunner

EXPOSE 8000
CMD bash -c "uwsgi --http :8000 --master --module init.wsgi --processes 4 --buffer-size 32768"
