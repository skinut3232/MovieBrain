import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { GenreCount } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: GenreCount[];
}

export default function GenreBreakdownChart({ data }: Props) {
  if (data.length === 0) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Genre Breakdown</h3>
      <ResponsiveContainer width="100%" height={Math.max(250, data.length * 28)}>
        <BarChart data={data} layout="vertical" margin={{ left: 10 }}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke={GRID_STROKE}
            horizontal={false}
          />
          <XAxis
            type="number"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            allowDecimals={false}
          />
          <YAxis
            dataKey="genre"
            type="category"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            width={80}
          />
          <Tooltip {...TOOLTIP_STYLE} />
          <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
