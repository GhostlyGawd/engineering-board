FROM python:3.14.7-slim-bookworm@sha256:ff4ceef5258b9303b40c004af0bd31ac82c6248a6b951f9d9b329bf456f1f4b7 AS python
FROM node:26.7.0-bookworm-slim@sha256:c00614442a3c693109886209462dd1b15462f6726347fa9cb9fc0125ca26f275 AS node
FROM buildpack-deps:bookworm-scm@sha256:f6a68ca746470d6eda3dcffe2e9852556d82b2476ac337fda49a944151d18952

COPY --from=python /usr/local/ /usr/local/
COPY --from=node /usr/lib/x86_64-linux-gnu/libatomic.so.1* /usr/lib/x86_64-linux-gnu/

RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode \
    && mkdir -p /workspaces/engineering-board \
        /opt/engineering-board-bootstrap \
        /opt/engineering-board-tools \
    && chown -R vscode:vscode \
        /workspaces \
        /opt/engineering-board-bootstrap \
        /opt/engineering-board-tools

COPY --chown=vscode:vscode scripts/bootstrap_dev.py /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py
COPY --chown=vscode:vscode support/dev-tools /opt/engineering-board-bootstrap/support/dev-tools

USER vscode

RUN python3 /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py \
      --root /opt/engineering-board-bootstrap \
      --install-root /opt/engineering-board-tools

ENV ENGINEERING_BOARD_DEV_TOOLS=/opt/engineering-board-tools
ENV PATH="/opt/engineering-board-tools/bin:/opt/engineering-board-tools/python-tools/bin:/opt/engineering-board-tools/node/bin:/opt/engineering-board-tools/node-tools/node_modules/.bin:${PATH}"

WORKDIR /workspaces/engineering-board
