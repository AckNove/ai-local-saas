import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import * as merchantApi from "../api/merchant";

export interface MerchantFormProps {
  /** 非空为编辑模式，仅编辑标量字段；空为新增模式，可填门店。 */
  initial: merchantApi.Merchant | null;
  onSubmit: (
    body: merchantApi.MerchantCreate | merchantApi.MerchantUpdate
  ) => Promise<void>;
  onCancel: () => void;
  submitting?: boolean;
}

export default function MerchantForm({ initial, onSubmit, onCancel, submitting }: MerchantFormProps) {
  const isEdit = !!initial;
  const [name, setName] = useState(initial?.name ?? "");
  const [industry, setIndustry] = useState(initial?.industry ?? "");
  const [address, setAddress] = useState(initial?.address ?? "");
  const [contact, setContact] = useState(initial?.contact ?? "");
  const [phone, setPhone] = useState(initial?.phone ?? "");
  const [pkg, setPkg] = useState(initial?.package ?? "");
  const [expire, setExpire] = useState(initial?.expire_time ?? "");
  const [stores, setStores] = useState<merchantApi.StoreIn[]>(
    isEdit ? [] : [{ name: "", location: "", video_account: "", poi_status: "" }]
  );

  const updateStore = (idx: number, key: keyof merchantApi.StoreIn, value: string) => {
    setStores((prev) => prev.map((s, i) => (i === idx ? { ...s, [key]: value } : s)));
  };

  const addStore = () => {
    setStores((prev) => [...prev, { name: "", location: "", video_account: "", poi_status: "" }]);
  };

  const removeStore = (idx: number) => {
    setStores((prev) => prev.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isEdit) {
      const body: merchantApi.MerchantUpdate = {
        name,
        industry,
        address,
        contact,
        phone,
        package: pkg,
        expire_time: expire,
      };
      await onSubmit(body);
    } else {
      const body: merchantApi.MerchantCreate = {
        name,
        industry,
        address,
        contact,
        phone,
        package: pkg,
        expire_time: expire,
        stores: stores.filter((s) => s.name.trim().length > 0),
      };
      await onSubmit(body);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-1.5">
        <Label>商家名称 *</Label>
        <Input value={name} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label>行业</Label>
          <Input value={industry} onChange={(e) => setIndustry(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>联系人</Label>
          <Input value={contact} onChange={(e) => setContact(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>联系电话</Label>
          <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </div>
        <div className="space-y-1.5">
          <Label>套餐</Label>
          <Input value={pkg} onChange={(e) => setPkg(e.target.value)} />
        </div>
      </div>
      <div className="space-y-1.5">
        <Label>地址</Label>
        <Input value={address} onChange={(e) => setAddress(e.target.value)} />
      </div>
      <div className="space-y-1.5">
        <Label>到期时间</Label>
        <Input value={expire} onChange={(e) => setExpire(e.target.value)} placeholder="如 2025-12-31" />
      </div>

      {!isEdit && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>初始门店</Label>
            <Button type="button" variant="outline" size="sm" onClick={addStore}>
              添加门店
            </Button>
          </div>
          {stores.map((s, idx) => (
            <div key={idx} className="rounded-md border border-slate-200 p-3 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">门店 #{idx + 1}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeStore(idx)}
                >
                  移除
                </Button>
              </div>
              <Input
                placeholder="门店名称"
                value={s.name}
                onChange={(e) => updateStore(idx, "name", e.target.value)}
              />
              <Input
                placeholder="位置"
                value={s.location}
                onChange={(e) => updateStore(idx, "location", e.target.value)}
              />
              <Input
                placeholder="视频号账号"
                value={s.video_account}
                onChange={(e) => updateStore(idx, "video_account", e.target.value)}
              />
              <Input
                placeholder="POI 状态"
                value={s.poi_status}
                onChange={(e) => updateStore(idx, "poi_status", e.target.value)}
              />
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          取消
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "提交中…" : isEdit ? "保存" : "创建"}
        </Button>
      </div>
    </form>
  );
}
