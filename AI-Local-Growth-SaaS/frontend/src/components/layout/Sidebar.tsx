import { NavLink } from "react-router-dom";
import { cn } from "../../utils/cn";
import type { CurrentUser } from "../../hooks/useAuth";

interface NavItem {
  to: string;
  label: string;
  roles: CurrentUser["role"][];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/dashboard", label: "数据概览", roles: ["admin", "merchant", "agent"] },
  { to: "/merchants", label: "商家管理", roles: ["admin"] },
  { to: "/seed-cards", label: "种草卡管理", roles: ["admin", "merchant", "agent"] },
  { to: "/ai/report", label: "AI 诊断报告", roles: ["admin", "merchant", "agent"] },
  { to: "/ai/comment", label: "AI 评论生成", roles: ["admin", "merchant", "agent"] },
  { to: "/ai/content", label: "AI 内容生成", roles: ["admin", "merchant", "agent"] },
];

export interface SidebarProps {
  user: CurrentUser | null;
}

export default function Sidebar({ user }: SidebarProps) {
  const role = user?.role ?? "merchant";
  const items = NAV_ITEMS.filter((item) => item.roles.includes(role));

  return (
    <aside className="flex h-full w-60 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-16 items-center justify-center border-b border-slate-200">
        <span className="text-base font-semibold text-slate-900">AI 商家增长</span>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-slate-900 text-white"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-slate-200 px-4 py-3 text-xs text-slate-400">
        本地商家增长 SaaS · v1.0
      </div>
    </aside>
  );
}
