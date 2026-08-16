import * as React from "react";
import { cn } from "../../utils/cn";

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  description?: React.ReactNode;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

/** 轻量模态弹窗（无外部依赖）。点击遮罩或关闭按钮触发 onClose。 */
export function Dialog({ open, onClose, title, description, children, footer, className }: DialogProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        className={cn(
          "relative z-10 w-full max-w-lg rounded-lg border border-slate-200 bg-white p-6 shadow-lg max-h-[90vh] overflow-y-auto",
          className
        )}
      >
        {title ? <h2 className="text-lg font-semibold text-slate-900">{title}</h2> : null}
        {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
        {title || description ? <div className="mt-4" /> : null}
        <div>{children}</div>
        {footer ? <div className="mt-6 flex justify-end gap-2">{footer}</div> : null}
      </div>
    </div>
  );
}
