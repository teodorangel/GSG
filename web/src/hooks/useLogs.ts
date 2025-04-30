import { useEffect, useState } from 'react';

/**
 * Hook to subscribe to log messages for a given crawl job via WebSocket
 * @param jobId string job identifier
 */
export function useLogs(jobId: string) {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    let ws: WebSocket | undefined;
    try {
      if (!jobId) {
        console.log('useLogs: no jobId, skipping WS.');
        return;
      }
      // Determine API base URL (NEXT_PUBLIC_API_URL or localhost:8000)
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
      const wsProtocol = apiBase.startsWith('https') ? 'wss' : 'ws';
      const wsUrl = apiBase.replace(/^https?/, wsProtocol) + `/logs/ws/${jobId}/`;
      console.log(`useLogs: connecting to WS ${wsUrl}`);
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('useLogs: WS connection opened');
        setLogs((prev) => [...prev, '🟢 WS connected']);
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          const ts = new Date(msg.timestamp).toLocaleTimeString();
          const text = `[${ts}] ${msg.status}: ${msg.url}`;
          setLogs((prev) => [...prev, text]);
        } catch (e) {
          console.warn('useLogs: message parse error', e);
          setLogs((prev) => [...prev, event.data]);
        }
      };

      ws.onerror = (event) => {
        console.warn('useLogs: WS error', event);
        setLogs((prev) => [...prev, '❌ WS error occurred']);
      };

      ws.onclose = (event) => {
        console.log('useLogs: WS connection closed', event);
        setLogs((prev) => [...prev, '🔴 WS closed']);
      };
    } catch (err) {
      console.warn('useLogs: unexpected error in WS setup', err);
      setLogs((prev) => [...prev, '❌ WS setup error']);
    }
    return () => {
      if (ws) {
        console.log('useLogs: cleaning up WS subscription');
        ws.close();
      }
    };
  }, [jobId]);

  return logs;
}