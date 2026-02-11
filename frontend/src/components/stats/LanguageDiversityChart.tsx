import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import type { LanguageCount } from '../../types';
import { TOOLTIP_STYLE, COLORS } from './chartTheme';

interface Props {
  data: LanguageCount[];
}

const langNames = new Intl.DisplayNames(['en'], { type: 'language' });

function getLanguageLabel(code: string): string {
  try {
    return langNames.of(code) ?? code.toUpperCase();
  } catch {
    return code.toUpperCase();
  }
}

export default function LanguageDiversityChart({ data }: Props) {
  if (data.length === 0) return null;

  const formatted = data.map((d) => ({
    ...d,
    label: getLanguageLabel(d.language),
  }));

  return (
    <div className="bg-gray-800 rounded-xl p-5">
      <h3 className="text-lg font-semibold mb-4">Languages</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={formatted}
            dataKey="count"
            nameKey="label"
            cx="50%"
            cy="50%"
            outerRadius={100}
            label={({ label, percent }) =>
              `${label} ${(percent * 100).toFixed(0)}%`
            }
            labelLine={false}
          >
            {formatted.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip {...TOOLTIP_STYLE} />
          <Legend
            formatter={(value: string) => (
              <span className="text-gray-300 text-sm">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
