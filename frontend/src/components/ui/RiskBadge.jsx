export default function RiskBadge({ level }) {
  const map = {
    High: "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
    Medium: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    Low: "bg-teal-100 text-teal-700 dark:bg-teal-950 dark:text-teal-300",
  };
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${map[level] || map.Low}`}>{level}</span>;
}
