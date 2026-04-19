"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type { RealtimeEvent } from "@/lib/types";

type Status = "connecting" | "connected" | "disconnected" | "error";

export function useWebSocket(path = "/ws/realtime") {
  const wsRef = useRef<WebSocket | null>(null);
  const [status, setStatus] = useState<Status>("disconnected");
  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    const wsBase = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";
    const url = `${wsBase}${path}`;

    setStatus("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setStatus("connected");

    ws.onmessage = (ev) => {
      try {
        const event = JSON.parse(ev.data as string) as RealtimeEvent;
        if (event.type !== "heartbeat") setLastEvent(event);
      } catch {
        // ignore malformed frames
      }
    };

    ws.onerror = () => setStatus("error");

    ws.onclose = () => {
      setStatus("disconnected");
      // Exponential-ish reconnect: 3s
      reconnectTimer.current = setTimeout(connect, 3000);
    };
  }, [path]);

  useEffect(() => {
    connect();
    return () => {
      reconnectTimer.current && clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { status, lastEvent };
}
