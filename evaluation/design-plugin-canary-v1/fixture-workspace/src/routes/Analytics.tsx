import { useRef, useState } from "react";
import { analyticsSeries } from "../data";
import { Drawer } from "../ui/Drawer";
import { Tabs } from "../ui/Tabs";

export function Analytics() {
  const [tab, setTab] = useState("Overview");
  const [range, setRange] = useState("Last 7 days");
  const [open, setOpen] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  return <main><h1>Northstar analytics starter</h1><Tabs value={tab} onValueChange={setTab}/><label>Date range <select value={range} onChange={event => setRange(event.target.value)}><option>Last 7 days</option><option>Last 30 days</option></select></label><p>Starter data: {analyticsSeries.join(", ")}</p><div data-chart-placeholder="true">Implement the reference screen and chart here.</div><button onClick={() => setOpen(true)}>Open starter drawer</button><Drawer open={open} onOpenChange={setOpen} initialFocusRef={heading}><p>Replace with the required details.</p></Drawer></main>;
}
