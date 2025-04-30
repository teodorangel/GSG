"use client";
import { useState } from "react";
import { useStartCrawl } from "@/hooks/useStartCrawl";
import { useLogs } from "@/hooks/useLogs";

export default function CrawlPage() {
  // Form state
  const [domain, setDomain] = useState("");
  const [depth, setDepth] = useState(1);
  const [concurrency, setConcurrency] = useState(2);
  const [delay, setDelay] = useState(1.0);

  // Mutation hook
  const { mutate: startCrawl, data: crawlData, status } = useStartCrawl();
  const isCrawling = status === "pending";

  // Once we have a jobId, subscribe to logs
  const jobId = crawlData?.job_id ?? "";
  const logs: string[] = useLogs(jobId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    startCrawl({ domain, depth, concurrency, delay });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-50 to-purple-50 p-6">
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-xl p-8 space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Start a Crawl Job</h1>

        <form
          onSubmit={handleSubmit}
          className="grid grid-cols-1 gap-6 bg-white p-8 rounded-lg shadow-lg"
        >
          <label className="block">
            <span className="text-gray-700 font-medium">Domain URL</span>
            <input
              type="url"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              placeholder="https://example.com"
              required
              className="mt-2 block w-full border border-gray-300 rounded-md p-2 placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </label>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <label className="block">
              <span className="text-gray-700 font-medium">Depth</span>
              <input
                type="number"
                value={depth}
                min={1}
                onChange={(e) => setDepth(Number(e.target.value))}
                className="mt-2 block w-full border border-gray-300 rounded-md p-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
            <label className="block">
              <span className="text-gray-700 font-medium">Concurrency</span>
              <input
                type="number"
                value={concurrency}
                min={1}
                onChange={(e) => setConcurrency(Number(e.target.value))}
                className="mt-2 block w-full border border-gray-300 rounded-md p-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
            <label className="block">
              <span className="text-gray-700 font-medium">Delay (seconds)</span>
              <input
                type="number"
                step="0.1"
                value={delay}
                min={0}
                onChange={(e) => setDelay(Number(e.target.value))}
                className="mt-2 block w-full border border-gray-300 rounded-md p-2 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={isCrawling}
            className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md disabled:opacity-50"
          >
            {isCrawling ? "Starting..." : "Start Crawl"}
          </button>
        </form>

        {/* Feedback: request sent and logs */}
        {status === "pending" && (
          <p className="text-gray-700 italic text-center">✔️ Request sent, awaiting job ID...</p>
        )}
        {jobId && (
          <section className="bg-gray-100 p-6 rounded-lg shadow-lg space-y-4">
            <p className="text-indigo-600 font-medium animate-pulse">
              🚀 Crawl started! Job ID: {jobId}
            </p>
            <h2 className="text-xl font-semibold text-gray-800">Logs for job {jobId}</h2>
            <div className="h-64 overflow-auto bg-gray-900 text-green-200 p-4 font-mono text-sm rounded-md space-y-1">
              {logs.length === 0 ? (
                <span className="text-green-200 font-medium italic">⌛ Waiting for logs...</span>
              ) : (
                <div className="w-full">
                  {logs.map((log, idx) => (
                    <div key={idx} className="mb-1">
                      {log}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}