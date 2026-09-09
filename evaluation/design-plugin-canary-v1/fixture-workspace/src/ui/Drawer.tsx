import { useEffect, useRef, type ReactNode, type RefObject } from "react";

export function Drawer({ open, onOpenChange, initialFocusRef, children }: { open: boolean; onOpenChange(value: boolean): void; initialFocusRef: RefObject<HTMLHeadingElement | null>; children: ReactNode }) {
  const returnFocus = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!open) return;
    returnFocus.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    initialFocusRef.current?.focus();
    const onKeyDown = (event: KeyboardEvent) => { if (event.key === "Escape") onOpenChange(false); };
    document.addEventListener("keydown", onKeyDown);
    return () => { document.removeEventListener("keydown", onKeyDown); returnFocus.current?.focus(); };
  }, [open, initialFocusRef, onOpenChange]);
  if (!open) return null;
  return <aside className="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title"><button onClick={() => onOpenChange(false)}>Close</button><h2 id="drawer-title" ref={initialFocusRef} tabIndex={-1}>Member details</h2>{children}</aside>;
}
