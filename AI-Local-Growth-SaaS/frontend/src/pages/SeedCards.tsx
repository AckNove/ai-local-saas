import { useNavigate } from "react-router-dom";
import { useSeedCards } from "../hooks/useSeedCards";
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

const TARGET_TEXT: Record<string, string> = {
  video: "视频号",
  private: "私域",
  custom: "自定义",
};

export default function SeedCards() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const merchantId = user?.role === "merchant" ? user.merchant_id : null;
  const { items, total, page, size, loading, setPage } = useSeedCards(merchantId);

  const totalPages = Math.max(1, Math.ceil(total / size));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">种草卡管理</h1>
          <p className="mt-1 text-sm text-slate-500">共 {total} 张种草卡</p>
        </div>
        <Button onClick={() => navigate("/seed-cards/create")}>创建种草卡</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">种草卡列表</CardTitle>
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
                  <TableHead>类型</TableHead>
                  <TableHead>跳转目标</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead className="text-right">操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-slate-400">
                      暂无种草卡
                    </TableCell>
                  </TableRow>
                ) : (
                  items.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.id}</TableCell>
                      <TableCell className="font-medium text-brand-600">{c.name}</TableCell>
                      <TableCell>{c.type}</TableCell>
                      <TableCell>{TARGET_TEXT[c.target_type] ?? c.target_type}</TableCell>
                      <TableCell>
                        <Badge variant={statusToVariant(c.status)}>{statusToText(c.status)}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/seed-cards/${c.id}`)}
                        >
                          详情 / 二维码
                        </Button>
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
    </div>
  );
}
