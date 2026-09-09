import { AccountRecovery } from "./routes/AccountRecovery";
import { Analytics } from "./routes/Analytics";
import { Checkout } from "./routes/Checkout";
import { PricingGrid } from "./pricing/PricingGrid";

export function App() {
  const path = window.location.pathname;
  if (path === "/recover") return <AccountRecovery />;
  if (path === "/analytics") return <Analytics />;
  if (path === "/checkout") return <Checkout />;
  if (path === "/pricing") return <PricingGrid />;
  return <main><h1>Synthetic canary fixtures</h1><nav><a href="/recover">Recovery</a> · <a href="/analytics">Analytics</a> · <a href="/checkout">Checkout</a> · <a href="/pricing">Pricing</a></nav></main>;
}
