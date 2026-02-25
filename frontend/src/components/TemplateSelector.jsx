function TemplateSelector({ selected, onChange }) {
  const templates = [
    {
      id: 'ats_classic',
      name: 'ATS Classic',
      desc: 'Clean Calibri, traditional layout',
      preview: 'Aa',
      font: 'font-serif',
    },
    {
      id: 'modern',
      name: 'Modern',
      desc: 'Blue accents, Segoe UI font',
      preview: 'Aa',
      font: 'font-sans',
      accent: 'text-blue-600',
    },
    {
      id: 'compact',
      name: 'Compact',
      desc: 'Tight spacing, fits more content',
      preview: 'Aa',
      font: 'font-sans text-xs',
    },
  ];

  return (
    <div className="flex gap-3">
      {templates.map(t => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={`flex-1 p-3 rounded-lg border-2 transition-all text-center ${
            selected === t.id
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
          }`}
        >
          <div className={`text-2xl mb-1 ${t.accent || 'text-gray-900 dark:text-white'} ${t.font}`}>
            {t.preview}
          </div>
          <div className="text-sm font-medium text-gray-900 dark:text-white">{t.name}</div>
          <div className="text-xs text-gray-500 dark:text-gray-400">{t.desc}</div>
        </button>
      ))}
    </div>
  );
}

export default TemplateSelector;
