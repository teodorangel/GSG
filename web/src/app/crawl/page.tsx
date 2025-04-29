"use client";
import { useState } from 'react';
import { useStartCrawl } from '../../hooks/useStartCrawl';
import { useLogs } from '../../hooks/useLogs';

export default function CrawlPage() {
  const [domain, setDomain] = useState('');
  const [depth, setDepth] = useState(1);
  const [concurrency, setConcurrency] = useState(2);
  const [delay, setDelay] = useState(1);
  const [jobId, setJobId] = useState<string>('');

  const crawlMutation = useStartCrawl();
  const logs = useLogs(jobId);

  const handleStart = (e: React.FormEvent) => {
    e.preventDefault();
    crawlMutation.mutate(
      { domain, depth, concurrency, delay },
      {
        onSuccess: (data) => {
          setJobId(data.job_id);
        },
      }
    );
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Start Crawl</h1>
      <form onSubmit={handleStart} className="space-y-4 max-w-md">
        <div>
          <label className="block text-sm font-medium">Domain</label>
          <input
            type="text"
            className="mt-1 block w-full border rounded p-2"
            value={domain}
            onChange={(e) => setDomain(e.target.value)}
            placeholder="example.com"
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Depth</label>
          <input
            type="number"
            className="mt-1 block w-full border rounded p-2"
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            min={1}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Concurrency</label>
          <input
            type="number"
            className="mt-1 block w-full border rounded p-2"
            value={concurrency}
            onChange={(e) => setConcurrency(Number(e.target.value))}
            min={1}
          />
        </div>
        <div>
          <label className="block text-sm font-medium">Delay (s)</label>
          <input
            type="number"
            step="0.1"
            className="mt-1 block w-full border rounded p-2"
            value={delay}
            onChange={(e) => setDelay(Number(e.target.value))}
            min={0}
          />
        </div>
        <button
          type="submit"
          disabled={crawlMutation.isLoading}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          {crawlMutation.isLoading ? 'Starting...' : 'Start Crawl'}
        </button>
      </form>

      {jobId && (
        <div className="mt-6">
          <h2 className="text-lg font-medium">Job ID: {jobId}</h2>
        </div>
      )}

      {jobId && (
        <div className="mt-4 max-h-64 overflow-auto bg-gray-100 p-4 rounded">
          <h3 className="font-semibold mb-2">Live Logs</h3>
          <div className="space-y-1">
            {logs.map((line, idx) => (
              <div key={idx} className="text-sm font-mono">
                {line}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}