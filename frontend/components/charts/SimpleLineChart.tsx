'use client';

import { useLanguage } from '@/lib/contexts/LanguageContext';

interface DataPoint {
  label: string;
  value: number;
}

interface SimpleLineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  color?: string;
  title?: string;
}

export function SimpleLineChart({
  data,
  width = 600,
  height = 300,
  color = '#4F46E5',
  title,
}: SimpleLineChartProps) {
  const { t } = useLanguage();

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <p className="text-gray-500">{t.charts.noData}</p>
      </div>
    );
  }

  const padding = { top: 40, right: 30, bottom: 50, left: 50 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Найти min и max значения
  const values = data.map(d => d.value);
  const maxValue = Math.max(...values, 10); // минимум 10 для масштаба
  const minValue = Math.min(...values, 0);
  const valueRange = maxValue - minValue || 1;

  // Создать точки для линии
  const points = data.map((point, index) => {
    const x = padding.left + (index / (data.length - 1 || 1)) * chartWidth;
    const y = padding.top + chartHeight - ((point.value - minValue) / valueRange) * chartHeight;
    return { x, y, label: point.label, value: point.value };
  });

  // Создать path для линии
  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x},${p.y}`).join(' ');

  // Создать path для области под линией
  const areaPath = `${linePath} L ${points[points.length - 1].x},${padding.top + chartHeight} L ${points[0].x},${padding.top + chartHeight} Z`;

  // Grid lines (горизонтальные)
  const gridLines = [0, 0.25, 0.5, 0.75, 1].map(ratio => ({
    y: padding.top + chartHeight - ratio * chartHeight,
    value: Math.round(minValue + ratio * valueRange),
  }));

  return (
    <div className="bg-white p-6 rounded-lg border border-gray-200">
      {title && <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>}

      <svg width={width} height={height} className="overflow-visible">
        {/* Grid lines */}
        {gridLines.map((line, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={line.y}
              x2={padding.left + chartWidth}
              y2={line.y}
              stroke="#E5E7EB"
              strokeWidth="1"
            />
            <text
              x={padding.left - 10}
              y={line.y + 4}
              textAnchor="end"
              className="text-xs fill-gray-600"
            >
              {line.value}
            </text>
          </g>
        ))}

        {/* Area under line */}
        <path
          d={areaPath}
          fill={color}
          fillOpacity="0.1"
        />

        {/* Line */}
        <path
          d={linePath}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Points */}
        {points.map((point, i) => (
          <g key={i}>
            <circle
              cx={point.x}
              cy={point.y}
              r="4"
              fill={color}
              stroke="white"
              strokeWidth="2"
              className="cursor-pointer hover:r-6 transition-all"
            />
            {/* Tooltip on hover */}
            <title>{`${point.label}: ${point.value}`}</title>
          </g>
        ))}

        {/* X-axis labels */}
        {points.map((point, i) => {
          // Показываем каждую N-ю метку для читаемости
          const showLabel = data.length <= 10 || i % Math.ceil(data.length / 10) === 0 || i === data.length - 1;
          if (!showLabel) return null;

          return (
            <text
              key={i}
              x={point.x}
              y={padding.top + chartHeight + 20}
              textAnchor="middle"
              className="text-xs fill-gray-600"
            >
              {point.label}
            </text>
          );
        })}
      </svg>
    </div>
  );
}
