import type { ReactNode } from "react";
export function PlanCard({ id, featured, children }: { id: string; featured: boolean; children: ReactNode }) { return <article className="plan-card" data-plan={id} data-featured={featured}>{children}</article>; }
