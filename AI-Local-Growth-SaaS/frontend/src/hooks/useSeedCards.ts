import { useCallback, useEffect, useState } from "react";
import * as seedCardApi from "../api/seedCard";

const SIZE = 20;

/** 种草卡列表数据获取（与种草卡列表页契约对齐）。 */
export function useSeedCards(merchantId?: number | null) {
  const [items, setItems] = useState<seedCardApi.SeedCardSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const load = useCallback(async (p: number, mid?: number | null) => {
    setLoading(true);
    try {
      const data: seedCardApi.SeedCardList = await seedCardApi.getSeedCardList({
        page: p,
        size: SIZE,
        merchant_id: mid ?? undefined,
      });
      setItems(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, []);

  // page / merchantId 变化即重新拉取
  useEffect(() => {
    void load(page, merchantId);
  }, [load, page, merchantId]);

  return { items, total, page, size: SIZE, loading, setPage, load };
}
