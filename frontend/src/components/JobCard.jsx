function JobCard({ job, onStatusChange, onDelete, onViewDetails }) {
  const statusColors = {
    saved: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400',
    applied: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400',
    interviewing: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400',
    offered: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400',
    rejected: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400',
  };

  const scoreColor = (score) => {
    if (score >= 70) return 'text-green-600 dark:text-green-400';
    if (score >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-gray-900 dark:text-white truncate">{job.job_title}</h4>
          <p className="text-sm text-gray-600 dark:text-gray-400 truncate">{job.company_name || 'Company not specified'}</p>
        </div>
        {job.quick_score != null && (
          <span className={`text-lg font-bold ml-2 ${scoreColor(job.quick_score)}`}>
            {Math.round(job.quick_score)}%
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 mb-3">
        <span className={`px-2 py-0.5 rounded text-xs font-medium capitalize ${statusColors[job.status] || statusColors.saved}`}>
          {job.status}
        </span>
        {job.created_at && (
          <span className="text-xs text-gray-400">
            {new Date(job.created_at).toLocaleDateString()}
          </span>
        )}
      </div>

      {job.notes && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">{job.notes}</p>
      )}

      <div className="flex items-center gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
        <select
          value={job.status}
          onChange={e => onStatusChange(job.id, e.target.value)}
          className="text-xs px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300"
        >
          <option value="saved">Saved</option>
          <option value="applied">Applied</option>
          <option value="interviewing">Interviewing</option>
          <option value="offered">Offered</option>
          <option value="rejected">Rejected</option>
        </select>
        <button
          onClick={() => onViewDetails(job)}
          className="text-xs px-2 py-1 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded"
        >
          Details
        </button>
        <button
          onClick={() => onDelete(job.id)}
          className="text-xs px-2 py-1 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded ml-auto"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default JobCard;
