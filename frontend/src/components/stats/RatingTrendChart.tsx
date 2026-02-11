import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { MonthRating } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: MonthRating[];
}

export default function RatingTrendChart({ data }: Props) {
  if (data.length < 2) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Rating Trend</h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
          <XAxis
            dataKey="month"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            domain={[1, 10]}
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
          />
          <Tooltip {...TOOLTIP_STYLE} />
          <Line
            type="monotone"
            dataKey="avg_rating"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ fill: '#f59e0b', r: 3 }}
            name="Avg Rating"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
