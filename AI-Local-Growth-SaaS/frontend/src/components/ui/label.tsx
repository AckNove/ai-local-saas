import * as React from "react";
import { cn } from "../../utils/cn";

export const Label = React.forwardRef<HTMLLabelElement, React.LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, ...props }, ref) => (
    <label
      ref={ref}
      className={cn("text-sm font-medium text-slate-700 leading-none peer-disabled:opacity-70", className)}
      {...props}
    />
  )
);
Label.displayName = "Label";
