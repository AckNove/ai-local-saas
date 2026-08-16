import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as merchantApi from "../api/merchant";
import * as seedCardApi from "../api/seedCard";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select } from "../components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { toast } from "../utils/toast";

export default function SeedCardCreate() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const isMerchant = user?.role === "merchant";

  const [merchants, setMerchants] = useState<merchantApi.MerchantSummary[]>([]);
  const [merchantId, setMerchantId] = useState<number | "">(
    isMerchant && user?.merchant_id ? user.merchant_id : ""
  );
  const [name, setName] = useState("");
  const [type, setType] = useState<string>("二维码");
  const [targetType, setTargetType] = useState<string>("video");
  const [targetUrl, setTargetUrl] = useState("");
  const [nfcId, setNfcId] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    merchantApi
      .getMerchantList({ page: 1, size: 200 })
      .then((res) => setMerchants(res.items))
      .catch(() => {});
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (merchantId === "") {
      toast("请选择所属商家", "error");
      return;
    }
    if (!name.trim()) {
      toast("请填写卡片名称", "error");
      return;
    }
    setSubmitting(true);
    try {
      const card = await seedCardApi.createSeedCard({
        merchant_id: Number(merchantId),
        name: name.trim(),
        type,
        target_type: targetType,
        target_url: targetUrl.trim(),
        nfc_id: nfcId.trim() || null,
      });
      toast("创建成功", "success");
      navigate(`/seed-cards/${card.id}`);
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <button
          className="text-sm text-brand-600 hover:underline"
          onClick={() => navigate("/seed-cards")}
        >
          ← 返回种草卡列表
        </button>
        <h1 className="mt-1 text-2xl font-semibold text-slate-900">创建种草卡</h1>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="text-base">卡片信息</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label>所属商家 *</Label>
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
              <Label>卡片名称 *</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="如：门店A-探店种草" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <Label>卡片类型</Label>
                <Select value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="二维码">二维码</option>
                  <option value="NFC">NFC</option>
                </Select>
              </div>
              <div className="space-y-1.5">
                <Label>跳转目标类型</Label>
                <Select value={targetType} onChange={(e) => setTargetType(e.target.value)}>
                  <option value="video">视频号</option>
                  <option value="private">私域</option>
                  <option value="custom">自定义</option>
                </Select>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>跳转目标 URL</Label>
              <Input
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="如 https://channels.weixin.qq.com/..."
              />
            </div>
            {type === "NFC" && (
              <div className="space-y-1.5">
                <Label>NFC 标签 ID（可选）</Label>
                <Input value={nfcId} onChange={(e) => setNfcId(e.target.value)} placeholder="留空则仅生成二维码" />
              </div>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={() => navigate("/seed-cards")}>
                取消
              </Button>
              <Button type="submit" disabled={submitting}>
                {submitting ? "提交中…" : "创建"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
