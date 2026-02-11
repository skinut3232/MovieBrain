interface Props {
  totalMovies: number;
  avgRating: number | null;
  totalRuntimeMinutes: number;
  totalRewatches: number;
  uniqueLanguages: number;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-5 text-center">
      <div className="text-3xl font-bold text-amber-400">{value}</div>
      <div className="text-sm text-gray-400 mt-1">{label}</div>
    </div>
  );
}

export default function HeroStats({
  totalMovies,
  avgRating,
  totalRuntimeMinutes,
  totalRewatches,
  uniqueLanguages,
}: Props) {
  const hours = Math.round(totalRuntimeMinutes / 60);
  const days = (totalRuntimeMinutes / 1440).toFixed(1);

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
      <StatCard label="Movies Watched" value={totalMovies.toLocaleString()} />
      <StatCard
        label="Average Rating"
        value={avgRating !== null ? avgRating.toFixed(1) : '-'}
      />
      <StatCard
        label="Hours Watched"
        value={hours > 0 ? `${hours.toLocaleString()} (${days}d)` : '-'}
      />
      <StatCard label="Rewatches" value={totalRewatches.toLocaleString()} />
      <StatCard label="Languages" value={uniqueLanguages.toLocaleString()} />
    </div>
  );
}
