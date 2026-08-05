/**
 * Circular score gauge component.
 */
function ScoreGauge({ score, size = 100 }) {
  const normalizedScore = Math.min(Math.max(score || 0, 0), 100);
  const radius = (size - 12) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let color = 'text-red-500';
  if (normalizedScore >= 70) color = 'text-green-500';
  else if (normalizedScore >= 50) color = 'text-yellow-500';

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }} role="img" aria-label={`${Math.round(normalizedScore)}% match score`}>
      <svg aria-hidden="true" className="transform -rotate-90" width={size} height={size}>
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-gray-200 dark:text-gray-700"
        />
        {/* Score circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          className={color}
          style={{
            strokeDasharray: circumference,
            strokeDashoffset,
            transition: 'stroke-dashoffset 0.5s ease-in-out',
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className={`text-2xl font-bold ${color}`}>
          {Math.round(normalizedScore)}<span className="text-sm">%</span>
        </span>
      </div>
    </div>
  );
}

export default ScoreGauge;
