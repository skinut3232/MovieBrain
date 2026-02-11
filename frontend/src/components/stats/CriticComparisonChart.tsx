import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import type { CriticComparison } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: CriticComparison[];
  avgUserScore: number | null;
  avgCriticScore: number | null;
  avgDifference: number | null;
}

export default function CriticComparisonChart({
  data,
  avgUserScore,
  avgCriticScore,
  avgDifference,
}: Props) {
  if (data.length === 0) return null;

  // Show text summary instead of chart if too few points
  if (data.length < 3) {
    return (
      <div className="bg-gray-800 rounded-xl p-5">
        <h3 className="text-lg font-semibold mb-4">You vs Critics</h3>
        <p className="text-gray-400">
          Not enough rated movies with critic scores to show a comparison. Rate
          more movies to unlock this chart!
        </p>
      </div>
    );
  }

  const diffLabel =
    avgDifference !== null
      ? avgDifference > 0
        ? `+${avgDifference.toFixed(1)} above critics`
        : avgDifference < 0
          ? `${avgDifference.toFixed(1)} below critics`
          : 'Same as critics'
      : '';

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-2">You vs Critics</h3>
      <div className="flex gap-6 text-sm text-gray-400 mb-4">
        {avgUserScore !== null && <span>Your avg: {avgUserScore}</span>}
        {avgCriticScore !== null && <span>Critics avg: {avgCriticScore}</span>}
        {diffLabel && (
          <span
            className={
              avgDifference! > 0
                ? 'text-emerald-400'
                : avgDifference! < 0
                  ? 'text-red-400'
                  : 'text-gray-400'
            }
          >
            {diffLabel}
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart margin={{ bottom: 10, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
          <XAxis
            dataKey="critic_score"
            type="number"
            domain={[0, 100]}
            name="Critic Score"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            label={{
              value: 'Critic Score',
              position: 'insideBottom',
              offset: -5,
              fill: AXIS_TICK_COLOR,
            }}
          />
          <YAxis
            dataKey="user_score"
            type="number"
            domain={[0, 100]}
            name="Your Score"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            label={{
              value: 'Your Score',
              angle: -90,
              position: 'insideLeft',
              fill: AXIS_TICK_COLOR,
            }}
          />
          <Tooltip
            {...TOOLTIP_STYLE}
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload as CriticComparison;
              return (
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-2 text-sm">
                  <p className="font-semibold text-white">{d.primary_title}</p>
                  <p className="text-gray-400">
                    You: {d.user_score} | Critics: {d.critic_score.toFixed(0)}
                  </p>
                </div>
              );
            }}
          />
          <ReferenceLine
            segment={[
              { x: 0, y: 0 },
              { x: 100, y: 100 },
            ]}
            stroke="#6b7280"
            strokeDasharray="5 5"
          />
          <Scatter data={data} fill="#f59e0b" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
