import { useEffect, useState } from "react";
import * as merchantApi from "../api/merchant";
import * as aiApi from "../api/ai";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";

export default function AIReport() {
  const { user } = useAuth();
  const isMerchant = user?.role === "merchant";

  const [merchants, setMerchants] = useState<merchantApi.MerchantSummary[]>([]);
  const [merchantId, setMerchantId] = useState<number | "">(
    isMerchant && user?.merchant_id ? user.merchant_id : ""
  );
  const [storeId, setStoreId] = useState<string>("");
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<aiApi.ReportResult | null>(null);

  useEffect(() => {
    merchantApi
      .getMerchantList({ page: 1, size: 200 })
      .then((res) => setMerchants(res.items))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (merchantId === "") {
      return;
    }
    setSubmitting(true);
    try {
      const res = await aiApi.generateReport({
        merchant_id: Number(merchantId),
        store_id: storeId ? Number(storeId) : null,
      });
      setResult(res);
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">AI 商家诊断报告</h1>
        <p className="mt-1 text-sm text-slate-500">
          输入商家，生成现状 / 机会 / 方案的网页诊断报告（Mock 离线可跑）
        </p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle className="text-base">诊断参数</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label>商家 *</Label>
              <Select
                value={String(merchantId)}
                disabled={isMerchant}
                onChange={(e) => setMerchantId(e.target.value ? Number(e.target.value) : "")}
              >
                <option value="">请选择商家</option>
                {merchants.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>门店 ID（可选）</Label>
              <Input
                value={storeId}
                onChange={(e) => setStoreId(e.target.value)}
                placeholder="留空表示整店诊断"
              />
            </div>
            <div className="flex justify-end">
              <Button type="submit" disabled={submitting || merchantId === ""}>
                {submitting ? "生成中…" : "生成诊断报告"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">诊断结果</CardTitle>
            <Badge variant="default">评分 {result.report.score}</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-md bg-slate-50 p-4 text-sm text-slate-700">
              {result.report.summary}
            </div>
            <div className="space-y-3">
              {result.report.items.map((item, idx) => (
                <div key={idx} className="rounded-md border border-slate-200 p-3">
                  <div className="mb-1 text-sm font-semibold text-slate-900">{item.dimension}</div>
                  <div className="text-sm text-slate-600">
                    <span className="font-medium">现状：</span>
                    {item.finding}
                  </div>
                  <div className="mt-1 text-sm text-slate-600">
                    <span className="font-medium">建议：</span>
                    {item.suggestion}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
