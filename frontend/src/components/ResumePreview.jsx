/**
 * HTML resume preview component with iframe sandbox.
 */
function ResumePreview({ html }) {
  if (!html) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center text-gray-500">
        No preview available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
      <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 flex items-center justify-between">
        <span className="text-sm font-medium text-gray-600 dark:text-gray-300">Resume Preview</span>
        <span className="text-xs text-gray-400">ATS-optimized format</span>
      </div>
      <iframe
        srcDoc={html}
        className="w-full bg-white"
        style={{ minHeight: '800px', border: 'none' }}
        title="Resume Preview"
        sandbox="allow-same-origin"
      />
    </div>
  );
}

export default ResumePreview;
