import * as React from "react";

interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "outline";
}

export function Badge({
  variant = "default",
  className = "",
  children,
  ...props
}: BadgeProps) {
  const styles = {
    default:
      "bg-blue-600 text-white",
    secondary:
      "bg-zinc-700 text-white",
    outline:
      "border border-zinc-600 text-zinc-300",
  };

  return (
    <span
      className={`
        inline-flex
        items-center
        rounded-full
        px-2
        py-1
        text-xs
        font-medium
        ${styles[variant]}
        ${className}
      `}
      {...props}
    >
      {children}
    </span>
  );
}