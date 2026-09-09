import type { ButtonHTMLAttributes } from "react";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & { intent: "primary" | "secondary" };
export function Button({ intent, className = "", ...props }: Props) {
  return <button className={`button button-${intent} ${className}`} {...props} />;
}
