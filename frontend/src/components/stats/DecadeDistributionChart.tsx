import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import type { DecadeCount } from '../../types';
import { TOOLTIP_STYLE, AXIS_TICK_COLOR, GRID_STROKE } from './chartTheme';

interface Props {
  data: DecadeCount[];
}

export default function DecadeDistributionChart({ data }: Props) {
  if (data.length === 0) return null;

  const formatted = data.map((d) => ({
    ...d,
    label: `${d.decade}s`,
  }));

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Decades</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_STROKE} />
          <XAxis
            dataKey="label"
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
          />
          <YAxis
            tick={{ fill: AXIS_TICK_COLOR, fontSize: 12 }}
            allowDecimals={false}
          />
          <Tooltip {...TOOLTIP_STYLE} />
          <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
