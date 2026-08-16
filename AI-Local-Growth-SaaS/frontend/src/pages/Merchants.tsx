import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMerchants } from "../hooks/useMerchants";
import * as merchantApi from "../api/merchant";
import { useAuth } from "../hooks/useAuth";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
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
import { toast } from "../utils/toast";

export default function Merchants() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const navigate = useNavigate();
  const {
    items,
    total,
    page,
    size,
    keyword,
    loading,
    setPage,
    setKeyword,
    create,
    update,
    disable,
    remove,
  } = useMerchants();

  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<merchantApi.Merchant | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<merchantApi.MerchantSummary | null>(null);

  const openCreate = () => {
    setEditing(null);
    setFormOpen(true);
  };

  const openEdit = async (id: number) => {
    try {
      const full = await merchantApi.getMerchant(id);
      setEditing(full);
      setFormOpen(true);
    } catch {
      // toast by interceptor
    }
  };

  const handleSubmit = async (body: merchantApi.MerchantCreate | merchantApi.MerchantUpdate) => {
    setSubmitting(true);
    try {
      if (editing) {
        await update(editing.id, body as merchantApi.MerchantUpdate);
      } else {
        await create(body as merchantApi.MerchantCreate);
      }
      setFormOpen(false);
      setEditing(null);
    } catch {
      // toast by interceptor
    } finally {
      setSubmitting(false);
    }
  };

  const handleDisable = async (m: merchantApi.MerchantSummary) => {
    const willDisable = m.status !== "disabled";
    if (!window.confirm(`确定要${willDisable ? "禁用" : "启用"}商家「${m.name}」吗？`)) return;
    try {
      await disable(m.id, willDisable);
    } catch {
      // toast by interceptor
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await remove(deleteTarget.id);
      setDeleteTarget(null);
    } catch {
      // toast by interceptor
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / size));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">商家管理</h1>
          <p className="mt-1 text-sm text-slate-500">共 {total} 个商家</p>
        </div>
        <Button onClick={openCreate}>新增商家</Button>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <CardTitle className="text-base">商家列表</CardTitle>
          <Input
            className="max-w-xs"
            placeholder="搜索名称 / 联系人 / 电话"
            value={keyword}
            onChange={(e) => {
              setKeyword(e.target.value);
              setPage(1);
            }}
          />
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-slate-400">加载中…</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>名称</TableHead>
                  <TableHead>行业</TableHead>
                  <TableHead>门店数</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-slate-400">
                      暂无商家
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((m) => (
                    <TableRow key={m.id}>
                      <TableCell>{m.id}</TableCell>
                      <TableCell>
                        <button
                          className="font-medium text-brand-600 hover:underline"
                          onClick={() => navigate(`/merchants/${m.id}`)}
                        >
                          {m.name}
                        </button>
                      </TableCell>
                      <TableCell>{m.industry || "-"}</TableCell>
                      <TableCell>{m.store_count}</TableCell>
                      <TableCell>
                        <Badge variant={statusToVariant(m.status)}>{statusToText(m.status)}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button size="sm" variant="outline" onClick={() => openEdit(m.id)}>
                            编辑
                          </Button>
                          {isAdmin && (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleDisable(m)}>
                                {m.status === "disabled" ? "启用" : "禁用"}
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => setDeleteTarget(m)}
                              >
                                删除
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}

          {totalPages > 1 && (
            <div className="mt-4 flex items-center justify-end gap-2 text-sm">
              <Button
                size="sm"
                variant="outline"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
              >
                上一页
              </Button>
              <span className="text-slate-500">
                {page} / {totalPages}
              </span>
              <Button
                size="sm"
                variant="outline"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                下一页
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog
        open={formOpen}
        onClose={() => setFormOpen(false)}
        title={editing ? `编辑商家 #${editing.id}` : "新增商家"}
      >
        <MerchantForm
          initial={editing}
          onSubmit={handleSubmit}
          onCancel={() => setFormOpen(false)}
          submitting={submitting}
        />
      </Dialog>

      <Dialog
        open={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        title="确认删除"
        footer={
          <>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              确认删除
            </Button>
          </>
        }
      >
        <p className="text-sm text-slate-600">
          确定要删除商家「{deleteTarget?.name}」吗？该操作仅软删除（不物理删除）。
        </p>
      </Dialog>
    </div>
  );
}
