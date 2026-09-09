export function Tabs({ value, onValueChange }: { value: string; onValueChange(value: string): void }) {
  return <div role="tablist" aria-label="Analytics view">{["Overview", "Activity"].map(tab => <button key={tab} role="tab" aria-selected={value === tab} onClick={() => onValueChange(tab)}>{tab}</button>)}</div>;
}
