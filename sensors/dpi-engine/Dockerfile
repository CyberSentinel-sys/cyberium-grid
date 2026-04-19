FROM golang:1.23-alpine AS builder

RUN apk add --no-cache libpcap-dev build-base

WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=1 go build -o /dpi-engine -ldflags="-s -w" ./main.go

# ── Runtime image ────────────────────────────────────────────────────────────
FROM alpine:3.20

RUN apk add --no-cache libpcap ca-certificates

COPY --from=builder /dpi-engine /usr/local/bin/dpi-engine

# NET_ADMIN, NET_RAW: required for raw packet capture via libpcap
# SYS_ADMIN: required for AF_XDP on Linux ≥4.18
# These capabilities must be granted at container runtime via docker-compose or k8s securityContext.

EXPOSE 9090

ENTRYPOINT ["/usr/local/bin/dpi-engine"]
CMD ["--output-mode", "nats", "--nats-url", "nats://nats:4222"]
