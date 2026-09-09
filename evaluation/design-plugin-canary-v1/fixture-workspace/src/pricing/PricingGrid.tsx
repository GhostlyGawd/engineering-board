import { plans } from "../data";
import { BillingToggle } from "./BillingToggle";
import { FeatureList } from "./FeatureList";
import { PlanCard } from "./PlanCard";
import { UnrelatedTrustSection } from "./UnrelatedTrustSection";
import "./pricing.css";

export function PricingGrid() {
  const featuredPlanId = "explorer";
  return <main><h1>Common Thread pricing</h1><BillingToggle/><section className="pricing-grid">{plans.map(plan => <PlanCard id={plan.id} featured={plan.id === featuredPlanId} key={plan.id}><h2>{plan.name}</h2><strong>{plan.price}/year</strong><FeatureList features={plan.features}/></PlanCard>)}</section><UnrelatedTrustSection /></main>;
}
