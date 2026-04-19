FROM rust:1.80-alpine AS builder

RUN apk add --no-cache musl-dev

WORKDIR /build
COPY Cargo.toml Cargo.lock* ./
# Cache dependencies layer.
RUN mkdir src && echo "fn main() {}" > src/main.rs && cargo build --release 2>/dev/null || true
RUN rm -rf src

COPY src/ ./src/
COPY policy/ ./policy/
RUN cargo build --release

# ── Runtime image ────────────────────────────────────────────────────────────
FROM alpine:3.20

RUN apk add --no-cache ca-certificates

COPY --from=builder /build/target/release/safety-gate /usr/local/bin/safety-gate
COPY --from=builder /build/policy /app/policy

WORKDIR /app

ENV POLICY_PATH=/app/policy/orhashield.rego
ENV NATS_URL=nats://nats:4222

ENTRYPOINT ["/usr/local/bin/safety-gate"]
