import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { Dialog } from "../ui/dialog";
import { toast } from "../../utils/toast";
import { changePassword } from "../../api/auth";
import type { CurrentUser } from "../../hooks/useAuth";

export interface TopbarProps {
  user: CurrentUser | null;
  onLogout: () => void;
}

const ROLE_TEXT: Record<string, string> = {
  admin: "管理员",
  merchant: "商家",
  agent: "代理",
};

export default function Topbar({ user, onLogout }: TopbarProps) {
  const navigate = useNavigate();
  const [pwdOpen, setPwdOpen] = useState(false);
  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleLogout = () => {
    onLogout();
    navigate("/login", { replace: true });
  };

  const handleChangePwd = async () => {
    if (!oldPwd || !newPwd) {
      toast("请填写原密码和新密码", "error");
      return;
    }
    if (newPwd.length < 6) {
      toast("新密码至少 6 位", "error");
      return;
    }
    if (newPwd !== confirmPwd) {
      toast("两次输入的新密码不一致", "error");
      return;
    }
    setSubmitting(true);
    try {
      await changePassword(oldPwd, newPwd);
      toast("密码修改成功", "success");
      setPwdOpen(false);
      setOldPwd("");
      setNewPwd("");
      setConfirmPwd("");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "修改失败";
      toast(msg, "error");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6">
      <div className="text-sm text-slate-400">管理后台</div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-700">{user?.username ?? "未登录"}</span>
        <Badge variant="secondary">{ROLE_TEXT[user?.role ?? ""] ?? user?.role ?? ""}</Badge>
        <Button variant="outline" size="sm" onClick={() => setPwdOpen(true)}>
          修改密码
        </Button>
        <Button variant="outline" size="sm" onClick={handleLogout}>
          退出登录
        </Button>
      </div>

      <Dialog open={pwdOpen} onClose={() => setPwdOpen(false)} title="修改密码">
        <div className="space-y-3">
          <div className="space-y-1.5">
            <Label>原密码</Label>
            <Input type="password" value={oldPwd} onChange={(e) => setOldPwd(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>新密码（至少 6 位）</Label>
            <Input type="password" value={newPwd} onChange={(e) => setNewPwd(e.target.value)} />
          </div>
          <div className="space-y-1.5">
            <Label>确认新密码</Label>
            <Input type="password" value={confirmPwd} onChange={(e) => setConfirmPwd(e.target.value)} />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setPwdOpen(false)}>取消</Button>
            <Button onClick={handleChangePwd} disabled={submitting}>
              {submitting ? "提交中…" : "确认修改"}
            </Button>
          </div>
        </div>
      </Dialog>
    </header>
  );
}
