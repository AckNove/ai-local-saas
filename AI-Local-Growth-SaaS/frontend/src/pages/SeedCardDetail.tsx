import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import * as seedCardApi from "../api/seedCard";
import { Button } from "../components/ui/button";
import { Badge, statusToText, statusToVariant } from "../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Label } from "../components/ui/label";
import { toast } from "../utils/toast";

const TARGET_TEXT: Record<string, string> = {
  video: "视频号",
  private: "私域",
  custom: "自定义",
};

export default function SeedCardDetail() {
  const { id } = useParams<{ id: string }>();
  const cardId = Number(id);
  const navigate = useNavigate();

  const [card, setCard] = useState<seedCardApi.SeedCard | null>(null);
  const [qrUrl, setQrUrl] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [qrLoading, setQrLoading] = useState(true);
  const objectUrlRef = useRef<string>("");

  useEffect(() => {
    setLoading(true);
    seedCardApi
      .getSeedCard(cardId)
      .then(setCard)
      .catch(() => {})
      .finally(() => setLoading(false));

    setQrLoading(true);
    seedCardApi
      .getSeedCardQrBlob(cardId)
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        objectUrlRef.current = url;
        setQrUrl(url);
      })
      .catch(() => {})
      .finally(() => setQrLoading(false));

    return () => {
      if (objectUrlRef.current) {
        URL.revokeObjectURL(objectUrlRef.current);
      }
    };
  }, [cardId]);

  const handleDownload = () => {
    if (!qrUrl) {
      toast("二维码尚未就绪", "error");
      return;
    }
    const a = document.createElement("a");
    a.href = qrUrl;
    a.download = `seed-card-${cardId}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (loading) return <div className="text-sm text-slate-500">加载中…</div>;
  if (!card) return <div className="text-sm text-slate-500">种草卡不存在</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <button
            className="text-sm text-brand-600 hover:underline"
            onClick={() => navigate("/seed-cards")}
          >
            ← 返回种草卡列表
          </button>
          <h1 className="mt-1 text-2xl font-semibold text-slate-900">{card.name}</h1>
        </div>
        <Badge variant={statusToVariant(card.status)}>{statusToText(card.status)}</Badge>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">卡片信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row label="ID" value={String(card.id)} />
            <Row label="商家 ID" value={String(card.merchant_id)} />
            <Row label="类型" value={card.type} />
            <Row label="跳转目标" value={TARGET_TEXT[card.target_type] ?? card.target_type} />
            <Row label="跳转 URL" value={card.target_url || "-"} />
            <Row label="slug" value={card.slug} />
            <Row label="NFC ID" value={card.nfc_id || "-"} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">二维码</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col items-center gap-4">
            {qrLoading ? (
              <p className="text-sm text-slate-400">二维码生成中…</p>
            ) : qrUrl ? (
              <img src={qrUrl} alt="种草卡二维码" className="h-48 w-48 rounded-md border border-slate-200" />
            ) : (
              <p className="text-sm text-slate-400">二维码生成失败</p>
            )}
            <div className="w-full space-y-1.5">
              <Label>落地页地址</Label>
              <p className="break-all rounded-md bg-slate-50 px-3 py-2 text-xs text-slate-600">
                /c/{card.slug}
              </p>
            </div>
            <Button onClick={handleDownload} disabled={!qrUrl}>
              下载二维码
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-100 py-1.5">
      <span className="text-slate-400">{label}</span>
      <span className="max-w-[60%] break-all text-right text-slate-700">{value}</span>
    </div>
  );
}
