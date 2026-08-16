import http from "./http";

export interface Store {
  id: number;
  merchant_id: number;
  name: string;
  location: string;
  video_account: string;
  poi_status: string;
  status: string;
}

export interface Merchant {
  id: number;
  name: string;
  industry: string;
  address: string;
  contact: string;
  phone: string;
  package: string;
  expire_time: string;
  status: string;
  created_at: string | null;
  stores: Store[];
}

export interface MerchantSummary {
  id: number;
  name: string;
  industry: string;
  status: string;
  store_count: number;
}

export interface MerchantList {
  items: MerchantSummary[];
  total: number;
}

export interface StoreIn {
  name: string;
  location?: string;
  video_account?: string;
  poi_status?: string;
}

export interface MerchantCreate {
  name: string;
  industry?: string;
  address?: string;
  contact?: string;
  phone?: string;
  package?: string;
  expire_time?: string;
  stores?: StoreIn[];
}

export interface MerchantUpdate {
  name?: string;
  industry?: string;
  address?: string;
  contact?: string;
  phone?: string;
  package?: string;
  expire_time?: string;
  status?: string;
}

export function createMerchant(body: MerchantCreate): Promise<Merchant> {
  return http.post("/merchant/create", body) as Promise<Merchant>;
}

export function getMerchantList(params: {
  page?: number;
  size?: number;
  keyword?: string;
}): Promise<MerchantList> {
  return http.get("/merchant/list", { params }) as Promise<MerchantList>;
}

export function getMerchant(id: number): Promise<Merchant> {
  return http.get(`/merchant/${id}`) as Promise<Merchant>;
}

export function updateMerchant(id: number, body: MerchantUpdate): Promise<Merchant> {
  return http.put(`/merchant/${id}`, body) as Promise<Merchant>;
}

export function disableMerchant(id: number, disabled: boolean): Promise<{ id: number; status: string }> {
  return http.post(`/merchant/${id}/disable`, { disabled }) as Promise<{ id: number; status: string }>;
}

export function deleteMerchant(id: number): Promise<{ id: number; status: string }> {
  return http.delete(`/merchant/${id}`) as Promise<{ id: number; status: string }>;
}
