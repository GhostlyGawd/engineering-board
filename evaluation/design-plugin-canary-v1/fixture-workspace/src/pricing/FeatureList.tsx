export function FeatureList({ features }: { features: readonly string[] }) { return <ul>{features.map(feature => <li key={feature}>{feature}</li>)}</ul>; }
