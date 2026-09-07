FROM --platform=linux/arm64 python:3.14.7-slim-bookworm@sha256:a110e01da17f27ebb99b4ae5d8fab540071fcf7bc906b2c8df29c925bb5d9e36 AS python-arm64
FROM --platform=linux/arm64 node:26.7.0-bookworm-slim@sha256:9e7720738fbcb12e8122beb5194cfa58ab0029c78c3ed39f8986aa68713e31bc AS node-arm64
FROM --platform=linux/arm64 buildpack-deps:bookworm-scm@sha256:4290d77f2efb22105839727af2a816a0aaba3ace690a10afd806e654bd78b1d3 AS tools-arm64

COPY --from=python-arm64 /usr/local/ /usr/local/
COPY --from=node-arm64 /usr/lib/aarch64-linux-gnu/libatomic.so.1* /usr/lib/aarch64-linux-gnu/

RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode \
    && mkdir -p /opt/engineering-board-bootstrap \
        /opt/engineering-board-runtime/linux-arm64 \
    && chown -R vscode:vscode \
        /opt/engineering-board-bootstrap \
        /opt/engineering-board-runtime

COPY --chown=vscode:vscode scripts/bootstrap_dev.py /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py
COPY --chown=vscode:vscode support/dev-tools /opt/engineering-board-bootstrap/support/dev-tools

USER vscode

ENV ENGINEERING_BOARD_DEV_TOOLS=/opt/engineering-board-runtime/linux-arm64

RUN python3 /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py \
      --root /opt/engineering-board-bootstrap \
      --install-root /opt/engineering-board-runtime/linux-arm64

FROM --platform=linux/amd64 python:3.14.7-slim-bookworm@sha256:ff4ceef5258b9303b40c004af0bd31ac82c6248a6b951f9d9b329bf456f1f4b7 AS python-amd64
FROM --platform=linux/amd64 node:26.7.0-bookworm-slim@sha256:c00614442a3c693109886209462dd1b15462f6726347fa9cb9fc0125ca26f275 AS node-amd64
FROM --platform=linux/amd64 buildpack-deps:bookworm-scm@sha256:f6a68ca746470d6eda3dcffe2e9852556d82b2476ac337fda49a944151d18952

COPY --from=python-amd64 /usr/local/ /usr/local/
COPY --from=node-amd64 /usr/lib/x86_64-linux-gnu/libatomic.so.1* /usr/lib/x86_64-linux-gnu/
COPY --from=tools-arm64 /lib/aarch64-linux-gnu/ /lib/aarch64-linux-gnu/
COPY --from=tools-arm64 /lib/ld-linux-aarch64.so.1 /lib/ld-linux-aarch64.so.1
COPY --from=tools-arm64 /usr/lib/aarch64-linux-gnu/ /usr/lib/aarch64-linux-gnu/
COPY --from=tools-arm64 /usr/bin/ /opt/engineering-board-native/usr/bin/
COPY --from=tools-arm64 /usr/lib/git-core/ /opt/engineering-board-native/usr/lib/git-core/
COPY --from=tools-arm64 /opt/engineering-board-runtime/linux-arm64/ /opt/engineering-board-runtime/linux-arm64/

RUN groupadd --gid 1000 vscode \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode \
    && mkdir -p /workspaces/engineering-board \
        /opt/engineering-board-bootstrap \
        /opt/engineering-board-runtime/linux-x86_64 \
    && chown -R vscode:vscode \
        /workspaces \
        /opt/engineering-board-bootstrap \
        /opt/engineering-board-runtime

COPY --chown=vscode:vscode scripts/bootstrap_dev.py /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py
COPY --chown=vscode:vscode support/dev-tools /opt/engineering-board-bootstrap/support/dev-tools
COPY --chown=vscode:vscode .devcontainer/select-toolchain.sh /usr/local/bin/select-toolchain.sh
RUN chmod 0755 /usr/local/bin/select-toolchain.sh

USER vscode

RUN if grep -Eq '(^|[[:space:]])asimd([[:space:]]|$)' /proc/cpuinfo; then \
      ENGINEERING_BOARD_DEVCONTAINER_EMULATED_BUILD=1 \
      python3 /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py \
        --root /opt/engineering-board-bootstrap \
        --install-root /opt/engineering-board-runtime/linux-x86_64 \
        --defer-executable-checks; \
    else \
      python3 /opt/engineering-board-bootstrap/scripts/bootstrap_dev.py \
        --root /opt/engineering-board-bootstrap \
        --install-root /opt/engineering-board-runtime/linux-x86_64; \
    fi

ENV ENGINEERING_BOARD_DEV_TOOLS=/opt/engineering-board-runtime/current
ENV PATH="/opt/engineering-board-runtime/current/bin:/opt/engineering-board-runtime/current/python-tools/bin:/opt/engineering-board-runtime/current/node/bin:/opt/engineering-board-runtime/current/node-tools/node_modules/.bin:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV GIT_CONFIG_COUNT=1
ENV GIT_CONFIG_KEY_0=safe.directory
ENV GIT_CONFIG_VALUE_0=/workspaces/engineering-board

WORKDIR /workspaces/engineering-board

ENTRYPOINT ["/usr/local/bin/select-toolchain.sh"]
