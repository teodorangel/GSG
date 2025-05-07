import { useEffect, useState } from 'react';
import type { LogMessage } from '@/types/log';

const MAX_RETRIES = 3;
const RETRY_DELAY = 2000; // 2 seconds

/**
 * Hook to subscribe to log messages for a given crawl job via WebSocket
 * @param jobId string job identifier
 */
export function useLogs(jobId: string) {
  const [logs, setLogs] = useState<LogMessage[]>([]);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    let ws: WebSocket | undefined;
    let retryTimeout: NodeJS.Timeout;

    const connect = () => {
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
          setRetryCount(0); // Reset retry count on successful connection
        setLogs((prev) => [...prev, {
          job_id: jobId,
          url: '',
          status: 'connected',
          detail: null,
          timestamp: new Date().toISOString()
        }]);
      };

      ws.onmessage = (event) => {
        try {
          const msg: LogMessage = JSON.parse(event.data);
          setLogs((prev) => [...prev, msg]);
        } catch (e) {
          console.warn('useLogs: message parse error', e);
            setLogs((prev) => [...prev, {
              job_id: jobId,
              url: '',
              status: 'error',
              detail: `Failed to parse message: ${e}`,
              timestamp: new Date().toISOString()
            }]);
        }
      };

        ws.onerror = (event: Event & { message?: string }) => {
        console.warn('useLogs: WS error', event);
        setLogs((prev) => [...prev, {
          job_id: jobId,
          url: '',
          status: 'error',
            detail: String((event as any).message ?? 'WebSocket connection error'),
          timestamp: new Date().toISOString()
        }]);
      };

      ws.onclose = (event) => {
        console.log('useLogs: WS connection closed', event);
        setLogs((prev) => [...prev, {
          job_id: jobId,
          url: '',
          status: 'closed',
            detail: event.reason || 'WebSocket connection closed',
          timestamp: new Date().toISOString()
        }]);
          // Attempt to reconnect if we haven't exceeded max retries
          if (retryCount < MAX_RETRIES) {
            setRetryCount(prev => prev + 1);
            retryTimeout = setTimeout(() => {
              console.log(`useLogs: attempting reconnect (${retryCount + 1}/${MAX_RETRIES})`);
              connect();
            }, RETRY_DELAY);
          }
      };
    } catch (err) {
      console.warn('useLogs: unexpected error in WS setup', err);
      setLogs((prev) => [...prev, {
        job_id: jobId,
        url: '',
        status: 'error',
        detail: String(err),
        timestamp: new Date().toISOString()
      }]);
    }
    };

    connect();

    return () => {
      if (ws) {
        console.log('useLogs: cleaning up WS subscription');
        ws.close();
      }
      if (retryTimeout) {
        clearTimeout(retryTimeout);
      }
    };
  }, [jobId, retryCount]);

  return logs;
}