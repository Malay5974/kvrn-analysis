export function DashboardSkeleton() {
  return <div className="dashboard-skeleton" aria-label="Loading analysis"><div className="skeleton skeleton--hero" /><div className="skeleton-grid">{Array.from({ length: 4 }, (_, index) => <div className="skeleton skeleton--card" key={index} />)}</div><div className="skeleton skeleton--chart" /></div>;
}
