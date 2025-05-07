export interface LogMessage {
  job_id: string;
  url: string;
  status: string;
  detail: unknown;
  timestamp: string;
} 