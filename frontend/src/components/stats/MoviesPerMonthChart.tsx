import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { MonthCount } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: MonthCount[];
}

export default function MoviesPerMonthChart({ data }: Props) {
  if (data.length < 2) return null;

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Watching Activity</h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
          <XAxis
            dataKey="month"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            allowDecimals={false}
          />
          <Tooltip {...TOOLTIP_STYLE} />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#3b82f6"
            fill="url(#blueGrad)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
