import * as React from "react";
import { cn } from "../../utils/cn";

type Variant = "default" | "secondary" | "success" | "warning" | "destructive" | "outline";

const variantClasses: Record<Variant, string> = {
  default: "bg-slate-900 text-white",
  secondary: "bg-slate-100 text-slate-700",
  success: "bg-green-100 text-green-700",
  warning: "bg-amber-100 text-amber-700",
  destructive: "bg-red-100 text-red-700",
  outline: "border border-slate-300 text-slate-600",
};

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: Variant;
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClasses[variant],
        className
      )}
      {...props}
    />
  );
}

/** 将后端 status 映射为展示语义。 */
export function statusToVariant(status: string): Variant {
  switch (status) {
    case "active":
      return "success";
    case "disabled":
      return "warning";
    case "deleted":
      return "destructive";
    default:
      return "secondary";
  }
}

export function statusToText(status: string): string {
  switch (status) {
    case "active":
      return "启用";
    case "disabled":
      return "禁用";
    case "deleted":
      return "已删除";
    default:
      return status;
  }
}
