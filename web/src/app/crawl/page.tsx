"use client";
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useStartCrawl, CrawlParams } from '@/hooks/useStartCrawl';
import { useLogs } from '@/hooks/useLogs';
import { useStopCrawl } from '@/hooks/useStopCrawl';

export default function CrawlPage() {
  // Form state
  const [domain, setDomain] = useState<string>('');
  const [depth, setDepth] = useState<number>(1);
  const [concurrency, setConcurrency] = useState<number>(2);
  const [delay, setDelay] = useState<number>(1.0);
  const [useProxies, setUseProxies] = useState<boolean>(false);

  // Mutation hook for starting crawl
  const { mutate: startCrawl, status } = useStartCrawl();
  const isSubmitting = status === 'pending';

  // Track active job ID and subscribe to logs
  const [jobId, setJobId] = useState<string>('');
  const logs = useLogs(jobId);
  const { mutate: stopCrawl, status: stopStatus } = useStopCrawl();

  const metrics = useMemo(() => {
    const latest = [...logs].reverse().find(l => l.status === 'progress');
    if (!latest) return null;
    try {
      const raw = typeof latest.detail === 'string' ? latest.detail : JSON.stringify(latest.detail ?? '{}');
      return JSON.parse(raw || '{}');
    } catch {
      return null;
    }
  }, [logs]);

  // Auto-scroll ref
  const endRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Form validation
  const isValid = /^https?:\/\/.+/.test(domain);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) return;
    const params: CrawlParams = { domain, depth, concurrency, delay, use_proxies: useProxies };
    startCrawl(params, {
      onSuccess: (data) => {
        setJobId(data.job_id);
      },
    });
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Start a Crawl Job</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium">Domain URL</label>
          <input
            type="url"
            className="mt-1 w-full border rounded p-2"
            placeholder="https://example.com"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            required
          />
          {!isValid && domain && <p className="text-red-600">Invalid URL</p>}
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block font-medium">Depth</label>
            <input
              type="number"
              className="mt-1 w-full border rounded p-2"
              min={1}
              value={depth}
              onChange={(e) => setDepth(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="block font-medium">Concurrency</label>
            <input
              type="number"
              className="mt-1 w-full border rounded p-2"
              min={1}
              value={concurrency}
              onChange={(e) => setConcurrency(Number(e.target.value))}
            />
          </div>
          <div>
            <label className="block font-medium">Delay (s)</label>
            <input
              type="number"
              step="0.1"
              className="mt-1 w-full border rounded p-2"
              min={0}
              value={delay}
              onChange={(e) => setDelay(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <input type="checkbox" id="useProxies" checked={useProxies} onChange={(e)=>setUseProxies(e.target.checked)} />
          <label htmlFor="useProxies" className="font-medium">Use proxies</label>
        </div>
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {isSubmitting ? 'Starting...' : 'Start Crawl'}
        </button>
        {jobId && (
          <button
            type="button"
            disabled={stopStatus === 'pending'}
            onClick={() =>
              stopCrawl(jobId, {
                onSuccess: () => setJobId(''),
              })
            }
            className="ml-4 px-4 py-2 bg-red-600 text-white rounded disabled:opacity-50"
          >
            {stopStatus === 'pending' ? 'Stopping...' : 'Stop Crawl'}
          </button>
        )}
      </form>

      {jobId && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold">Logs for Job {jobId.slice(0, 8)}</h2>
          <div className="mt-2 h-64 overflow-auto bg-gray-100 text-black p-4 font-mono text-sm">
            {logs.length === 0 ? (
              <p className="italic text-gray-600">Waiting for logs...</p>
            ) : (
              logs.map((log, idx) => {
                const detailStr =
                  typeof log.detail === 'string'
                    ? log.detail
                    : JSON.stringify(log.detail);
                const statusColor = (() => {
                  switch (log.status) {
                    case 'started':
                      return 'text-blue-600';
                    case 'fetched':
                      return 'text-indigo-700';
                    case 'ingested':
                      return 'text-green-700';
                    case 'progress':
                      return 'text-gray-700';
                    case 'error':
                      return 'text-red-600';
                    case 'stopped':
                      return 'text-yellow-700';
                    case 'completed':
                      return 'text-emerald-700';
                    default:
                      return 'text-gray-700';
                  }
                })();

                return (
                <div key={idx} className="mb-1">
                    <span className="text-gray-500">[
                      {new Date(log.timestamp).toLocaleString()}]
                    </span>{' '}
                    <span className={`font-semibold ${statusColor}`}>{log.status}</span>
                  {log.url && <>: {log.url}</>}
                    {detailStr && detailStr !== 'null' && (
                      <div className="pl-8 text-gray-600 whitespace-pre-wrap break-words">
                        {detailStr}
                      </div>
                    )}
                </div>
                );
              })
            )}
            <div ref={endRef} />
          </div>
        </div>
      )}

      {metrics && (
        <div className="mt-6 grid grid-cols-4 gap-4 text-center">
          <div className="bg-white p-4 rounded shadow">
            <div className="text-sm text-gray-500">Fetched</div>
            <div className="text-xl font-bold">{metrics.fetched}</div>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <div className="text-sm text-gray-500">Ingested</div>
            <div className="text-xl font-bold">{metrics.ingested}</div>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <div className="text-sm text-gray-500">Errors</div>
            <div className="text-xl font-bold text-red-600">{metrics.errors}</div>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <div className="text-sm text-gray-500">Elapsed (s)</div>
            <div className="text-xl font-bold">{metrics.elapsed.toFixed(1)}</div>
          </div>
        </div>
      )}
    </div>
  );
}