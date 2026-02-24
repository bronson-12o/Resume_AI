/**
 * Removable skill tag/chip component.
 */
const VARIANTS = {
  default: 'bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200',
  blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
  green: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
  red: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
};

function SkillTag({ name, onRemove, variant = 'default' }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${VARIANTS[variant] || VARIANTS.default}`}>
      {name}
      {onRemove && (
        <button
          onClick={onRemove}
          className="ml-0.5 hover:text-red-500 transition-colors"
          title="Remove"
        >
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </span>
  );
}

export default SkillTag;
