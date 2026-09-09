import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const read = path => readFile(new URL(`../${path}`, import.meta.url), "utf8");
test("all four deterministic routes are wired", async () => { const app = await read("src/App.tsx"); for (const route of ["/recover","/analytics","/checkout","/pricing"]) assert.match(app, new RegExp(route)); });
test("recovery implements five observable steps without answer annotations", async () => { const source = await read("src/routes/AccountRecovery.tsx"); for (const step of [1,2,3,4,5]) assert.match(source, new RegExp(`step === ${step}`)); assert.doesNotMatch(source, /discoverability|dead-end|screen-reader-name/); });
test("analytics starter leaves scored chart, crop, layout, and button use unsolved", async () => { const source = await read("src/routes/Analytics.tsx"); assert.match(source, /data-chart-placeholder/); assert.doesNotMatch(source, /<svg role="img"|intent="primary"|\/aurora\.svg|className="analytics"/); });
test("shared drawer implements focus entry, Escape close, and focus restoration", async () => { const source = await read("src/ui/Drawer.tsx"); assert.match(source, /initialFocusRef\.current\?\.focus/); assert.match(source, /event\.key === "Escape"/); assert.match(source, /returnFocus\.current\?\.focus/); });
test("checkout contains the deterministic flawed baseline", async () => { const [source, css] = await Promise.all([read("src/routes/Checkout.tsx"), read("src/styles.css")]); assert.match(source, /className="fake-select"/); assert.match(css, /height:720px;overflow:hidden/); });
test("pricing preserves locked unrelated copy in a separate component", async () => { const [source, locked] = await Promise.all([read("src/pricing/PricingGrid.tsx"),read("src/pricing/UnrelatedTrustSection.tsx")]); assert.match(locked, /Member-owned\. Locally rooted\. Clear prices\./); assert.match(source, /featuredPlanId = "explorer"/); for (const name of ["PlanCard","FeatureList","BillingToggle","UnrelatedTrustSection"]) assert.match(source,new RegExp(name)); });
