import http from "./http";

export interface SeedCard {
  id: number;
  merchant_id: number;
  name: string;
  slug: string;
  type: string;
  target_type: string;
  target_url: string;
  nfc_id: string | null;
  qr_code: string | null;
  status: string;
  created_at: string | null;
}

export interface SeedCardSummary {
  id: number;
  merchant_id: number;
  name: string;
  slug: string;
  type: string;
  target_type: string;
  target_url: string;
  status: string;
  created_at: string | null;
}

export interface SeedCardList {
  items: SeedCardSummary[];
  total: number;
}

export interface SeedCardCreate {
  merchant_id: number;
  name: string;
  type: string;
  target_type: string;
  target_url: string;
  nfc_id?: string | null;
}

export function createSeedCard(body: SeedCardCreate): Promise<SeedCard> {
  return http.post("/seed-card/create", body) as Promise<SeedCard>;
}

export function getSeedCardList(params: {
  page?: number;
  size?: number;
  merchant_id?: number | null;
}): Promise<SeedCardList> {
  return http.get("/seed-card/list", { params }) as Promise<SeedCardList>;
}

export function getSeedCard(id: number): Promise<SeedCard> {
  return http.get(`/seed-card/${id}`) as Promise<SeedCard>;
}

/** 获取二维码 PNG 二进制（用于展示与下载）。 */
export async function getSeedCardQrBlob(id: number): Promise<Blob> {
  const res = await http.get(`/seed-card/${id}/qrcode`, {
    responseType: "blob",
  });
  return res as unknown as Blob;
}
