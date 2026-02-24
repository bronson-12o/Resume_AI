/**
 * Skill gap recommendation card component.
 */
const PRIORITY_STYLES = {
  high: { bg: 'bg-red-50 dark:bg-red-900/20', border: 'border-red-200 dark:border-red-800', badge: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' },
  medium: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', border: 'border-yellow-200 dark:border-yellow-800', badge: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' },
  low: { bg: 'bg-blue-50 dark:bg-blue-900/20', border: 'border-blue-200 dark:border-blue-800', badge: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' },
};

function GapCard({ recommendation }) {
  const { skill, priority, reason, learning_path, estimated_time, curated_resource } = recommendation;
  const style = PRIORITY_STYLES[priority] || PRIORITY_STYLES.medium;

  return (
    <div className={`p-4 rounded-lg border ${style.bg} ${style.border}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-gray-900 dark:text-white">{skill}</span>
        <span className={`px-2 py-0.5 rounded text-xs font-medium ${style.badge}`}>
          {priority}
        </span>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{reason}</p>
      <p className="text-sm text-gray-700 dark:text-gray-300">{learning_path}</p>
      {estimated_time && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Estimated: {estimated_time}</p>
      )}
      {curated_resource && (
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
          <a
            href={curated_resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-primary-600 dark:text-primary-400 hover:underline"
          >
            {curated_resource.resource}
          </a>
        </div>
      )}
    </div>
  );
}

export default GapCard;
