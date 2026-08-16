import http from "./http";

export interface CommentResult {
  comments: string[];
  task_id: number;
}

export interface ReportItem {
  dimension: string;
  finding: string;
  suggestion: string;
}

export interface ReportData {
  score: number;
  summary: string;
  items: ReportItem[];
}

export interface ReportResult {
  report: ReportData;
  task_id: number;
}

export interface ContentResult {
  content: string;
  task_id: number;
}

export interface CommentIn {
  video: string;
  industry?: string;
}

export interface ReportIn {
  merchant_id: number;
  store_id?: number | null;
}

export interface ContentIn {
  type: "script" | "copy";
  industry?: string;
  topic: string;
  tone?: string | null;
}

export function generateComment(body: CommentIn): Promise<CommentResult> {
  return http.post("/ai/comment", body) as Promise<CommentResult>;
}

export function generateReport(body: ReportIn): Promise<ReportResult> {
  return http.post("/ai/report", body) as Promise<ReportResult>;
}

export function generateContent(body: ContentIn): Promise<ContentResult> {
  return http.post("/ai/content", body) as Promise<ContentResult>;
}
