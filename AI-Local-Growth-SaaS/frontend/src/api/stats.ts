import http from "./http";

export interface RecentEvent {
  card_id: number;
  event_type: string;
  created_at: string;
}

export interface TrendPoint {
  date: string;
  scan: number;
  click: number;
}

export interface StatsOverview {
  merchant_count: number;
  store_count: number;
  card_count: number;
  scan_total: number;
  click_total: number;
  share_total: number;
  comment_total: number;
  recent_events: RecentEvent[];
  trend: TrendPoint[];
}

export function getOverview(params?: { merchant_id?: number | null }): Promise<StatsOverview> {
  return http.get("/stats/overview", { params }) as Promise<StatsOverview>;
}
