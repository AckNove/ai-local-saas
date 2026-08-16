import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import * as merchantApi from "../api/merchant";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/button";
import { Badge, statusToText, statusToVariant } from "../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";
import { Dialog } from "../components/ui/dialog";
import MerchantForm from "../components/MerchantForm";

export default function MerchantDetail() {
  const { id } = useParams<{ id: string }>();
  const merchantId = Number(id);
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const navigate = useNavigate();

  const [merchant, setMerchant] = useState<merchantApi.Merchant | null>(null);
  const [loading, setLoading] = useState(true);
  const [formOpen, setFormOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const load = () => {
    setLoading(true);
    merchantApi
      .getMerchant(merchantId)
      .then(setMerchant)
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [merchantId]);

  const handleSubmit = async (body: merchantApi.MerchantCreate | merchantApi.MerchantUpdate) => {
    setSubmitting(true);
    try {
      await merchantApi.updateMerchant(merchantId, body as merchantApi.MerchantUpdate);
      setFormOpen(false);
      load();
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="text-sm text-slate-500">加载中…</div>;
  if (!merchant) return <div className="text-sm text-slate-500">商家不存在</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button
            className="text-sm text-brand-600 hover:underline"
            onClick={() => navigate("/merchants")}
          >
            ← 返回商家列表
          </button>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">{merchant.name}</h1>
        </div>
        {isAdmin && (
          <Button onClick={() => setFormOpen(true)}>编辑</Button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">基本信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row label="ID" value={String(merchant.id)} />
            <Row label="行业" value={merchant.industry || "-"} />
            <Row label="联系人" value={merchant.contact || "-"} />
            <Row label="电话" value={merchant.phone || "-"} />
            <Row label="地址" value={merchant.address || "-"} />
            <Row label="套餐" value={merchant.package || "-"} />
            <Row label="到期时间" value={merchant.expire_time || "-"} />
            <div className="flex items-center gap-2 pt-1">
              <span className="text-slate-400">状态</span>
              <Badge variant={statusToVariant(merchant.status)}>
                {statusToText(merchant.status)}
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">门店列表（{merchant.stores.length}）</CardTitle>
          </CardHeader>
          <CardContent>
            {merchant.stores.length === 0 ? (
              <p className="text-sm text-slate-400">暂无门店</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>名称</TableHead>
                    <TableHead>视频号</TableHead>
                    <TableHead>POI</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {merchant.stores.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>{s.name}</TableCell>
                      <TableCell>{s.video_account || "-"}</TableCell>
                      <TableCell>{s.poi_status || "-"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>

      <Dialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        title={`编辑商家 #${merchant.id}`}
      >
        <MerchantForm
          initial={merchant}
          onSubmit={handleSubmit}
          onCancel={() => setFormOpen(false)}
          submitting={submitting}
        />
      </Dialog>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-1.5">
      <span className="text-slate-400">{label}</span>
      <span className="text-slate-700">{value}</span>
    </div>
  );
}
