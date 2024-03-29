ARG NAUTOBOT_VER="1.3.1"
ARG PYTHON_VER=3.8

FROM ghcr.io/nautobot/nautobot-dev:${NAUTOBOT_VER}-py${PYTHON_VER}

ARG NAUTOBOT_ROOT=/opt/nautobot

ENV prometheus_multiproc_dir=/prom_cache
ENV NAUTOBOT_ROOT ${NAUTOBOT_ROOT}

WORKDIR $NAUTOBOT_ROOT

# Configure poetry
RUN poetry config virtualenvs.create false \
    && poetry config installer.parallel false

# -------------------------------------------------------------------------------------
# Install Nautobot Plugin
# -------------------------------------------------------------------------------------
WORKDIR /tmp/install

# Copy in only pyproject.toml/poetry.lock to help with caching this layer if no updates to dependencies
COPY poetry.lock pyproject.toml /tmp/install/

# Add the requested Nautobot version to pyproject
# to install the correct version based on the NAUTOBOT_VER argument
# Otherwise Poetry will override the version in this container
# with the one in the poetry.lock
# Redifine NAUTOBOT_VER as a build arg as initial is defined outside FROM.
ARG NAUTOBOT_VER="1.3.1"
RUN poetry add nautobot@$NAUTOBOT_VER

# --no-root declares not to install the project package since we're wanting to take advantage of caching dependency installation
# and the project is copied in and installed after this step
RUN poetry install --no-interaction --no-ansi --no-root

# Copy in the rest of the source code and install local Nautobot plugin
WORKDIR /source
COPY . /source
RUN cp /tmp/install/* /source/
RUN poetry install --no-interaction --no-ansi

COPY development/nautobot_config.py ${NAUTOBOT_ROOT}/nautobot_config.py
