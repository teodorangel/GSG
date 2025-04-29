import { useEffect, useState } from 'react';

/**
 * Hook to subscribe to log messages for a given crawl job via WebSocket
 * @param jobId string job identifier
 */
export function useLogs(jobId: string) {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    if (!jobId) return;
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}://${host}/logs/ws/${jobId}`);

    ws.onmessage = (event) => {
      setLogs((prev) => [...prev, event.data]);
    };
    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  return logs;
}