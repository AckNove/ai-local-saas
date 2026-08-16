import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import * as statsApi from "../api/stats";
import * as merchantApi from "../api/merchant";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

const EVENT_TEXT: Record<string, string> = {
  scan: "扫码",
  click: "点击",
  share: "分享",
  comment: "评论",
};

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<statsApi.StatsOverview | null>(null);
  const [myMerchant, setMyMerchant] = useState<merchantApi.Merchant | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    statsApi
      .getOverview()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // 商家视角：加载自己的商家详情（含门店）
  useEffect(() => {
    if (user?.role === "merchant" && user.merchant_id) {
      merchantApi
        .getMerchant(user.merchant_id)
        .then(setMyMerchant)
        .catch(() => {});
    }
  }, [user]);

  if (loading) {
    return <div className="text-sm text-slate-500">加载中…</div>;
  }
  if (!data) {
    return <div className="text-sm text-slate-500">暂无数据</div>;
  }

  const counts = [
    { label: "商家总数", value: data.merchant_count },
    { label: "门店总数", value: data.store_count },
    { label: "种草卡总数", value: data.card_count },
  ];

  const events = [
    { label: "扫码", value: data.scan_total },
    { label: "点击", value: data.click_total },
    { label: "分享", value: data.share_total },
    { label: "评论", value: data.comment_total },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">数据概览</h1>
        <p className="mt-1 text-sm text-slate-500">
          欢迎，{user?.username}（{user?.role === "admin" ? "管理员" : "商家"}）
          {user?.role !== "admin" ? " · 仅展示您名下数据" : ""}
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {counts.map((c) => (
          <Card key={c.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">{c.label}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-900">{c.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {user?.role === "merchant" && myMerchant && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">我的门店（{myMerchant.stores.length}）</CardTitle>
          </CardHeader>
          <CardContent>
            {myMerchant.stores.length === 0 ? (
              <p className="text-sm text-slate-400">暂无门店，请联系平台运营配置</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {myMerchant.stores.map((s) => (
                  <div key={s.id} className="rounded-md border border-slate-200 p-3 text-sm">
                    <div className="font-medium text-slate-900">{s.name}</div>
                    <div className="mt-1 text-slate-500">位置：{s.location || "-"}</div>
                    <div className="text-slate-500">视频号：{s.video_account || "-"}</div>
                    <div className="text-slate-500">POI：{s.poi_status || "未绑定"}</div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {events.map((e) => (
          <Card key={e.label}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">{e.label}次数</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-brand-600">{e.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">近 7 天互动趋势</CardTitle>
        </CardHeader>
        <CardContent>
          {data.trend.length === 0 ? (
            <p className="text-sm text-slate-400">暂无趋势数据</p>
          ) : (
            <TrendChart trend={data.trend} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">近期事件</CardTitle>
        </CardHeader>
        <CardContent>
          {data.recent_events.length === 0 ? (
            <p className="text-sm text-slate-400">暂无事件记录</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {data.recent_events.map((ev, idx) => (
                <li key={idx} className="flex items-center justify-between py-2 text-sm">
                  <span className="flex items-center gap-2">
                    <Badge variant="secondary">{EVENT_TEXT[ev.event_type] ?? ev.event_type}</Badge>
                    <span className="text-slate-600">种草卡 #{ev.card_id}</span>
                  </span>
                  <span className="text-slate-400">{ev.created_at}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <div className="flex gap-3">
        <Link
          to="/merchants"
          className="text-sm font-medium text-brand-600 hover:underline"
        >
          前往商家管理 →
        </Link>
        <Link
          to="/seed-cards"
          className="text-sm font-medium text-brand-600 hover:underline"
        >
          前往种草卡管理 →
        </Link>
      </div>
    </div>
  );
}

/** 纯 CSS 近 7 天趋势柱状图（扫码/点击双指标）。 */
function TrendChart({ trend }: { trend: statsApi.TrendPoint[] }) {
  const maxVal = Math.max(1, ...trend.map((t) => Math.max(t.scan, t.click)));
  const height = (v: number) => Math.max(4, Math.round((v / maxVal) * 80));

  return (
    <div>
      <div className="mb-2 flex items-center gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-sm bg-brand-600" /> 扫码
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block h-2 w-2 rounded-sm bg-slate-300" /> 点击
        </span>
      </div>
      <div className="flex items-end gap-2 h-28">
        {trend.map((t) => (
          <div key={t.date} className="flex flex-1 flex-col items-center gap-1">
            <div className="flex items-end gap-1 w-full justify-center">
              <div
                className="w-4 rounded-t bg-brand-600"
                style={{ height: `${height(t.scan)}px` }}
                title={`扫码 ${t.scan}`}
              />
              <div
                className="w-4 rounded-t bg-slate-300"
                style={{ height: `${height(t.click)}px` }}
                title={`点击 ${t.click}`}
              />
            </div>
            <span className="text-[10px] text-slate-400">{t.date.slice(5)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
