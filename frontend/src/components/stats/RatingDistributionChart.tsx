import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { RatingBucket } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: RatingBucket[];
}

export default function RatingDistributionChart({ data }: Props) {
  if (data.every((d) => d.count === 0)) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Rating Distribution</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
          <XAxis
            dataKey="rating"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
          />
          <YAxis
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            allowDecimals={false}
          />
          <Tooltip {...TOOLTIP_STYLE} />
          <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
