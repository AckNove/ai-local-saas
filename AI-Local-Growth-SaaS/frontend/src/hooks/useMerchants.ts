import { useCallback, useEffect, useState } from "react";
import * as merchantApi from "../api/merchant";

const SIZE = 20;

/** 商家列表数据获取 + 变更操作（与商家管理页契约对齐）。 */
export function useMerchants() {
  const [items, setItems] = useState<merchantApi.MerchantSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [keyword, setKeyword] = useState("");

  const load = useCallback(async (p: number, kw: string) => {
    setLoading(true);
    try {
      const data: merchantApi.MerchantList = await merchantApi.getMerchantList({
        page: p,
        size: SIZE,
        keyword: kw,
      });
      setItems(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, []);

  // page / keyword 变化即重新拉取
  useEffect(() => {
    void load(page, keyword);
  }, [load, page, keyword]);

  const create = useCallback(
    async (body: merchantApi.MerchantCreate) => {
      await merchantApi.createMerchant(body);
      setKeyword("");
      setPage(1);
      await load(1, "");
    },
    [load]
  );

  const update = useCallback(
    async (id: number, body: merchantApi.MerchantUpdate) => {
      await merchantApi.updateMerchant(id, body);
      await load(page, keyword);
    },
    [load, page, keyword]
  );

  const disable = useCallback(
    async (id: number, disabled: boolean) => {
      await merchantApi.disableMerchant(id, disabled);
      await load(page, keyword);
    },
    [load, page, keyword]
  );

  const remove = useCallback(
    async (id: number) => {
      await merchantApi.deleteMerchant(id);
      await load(page, keyword);
    },
    [load, page, keyword]
  );

  const search = useCallback(
    (kw: string) => {
      setKeyword(kw);
      setPage(1);
      void load(1, kw);
    },
    [load]
  );

  return {
    items,
    total,
    page,
    size: SIZE,
    keyword,
    loading,
    setPage,
    setKeyword,
    create,
    update,
    disable,
    remove,
    search,
  };
}
