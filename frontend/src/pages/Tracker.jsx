import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import JobCard from '../components/JobCard';
import { listProfiles, listSavedJobs, updateSavedJob, deleteSavedJob, getJobStats } from '../api/client';

const COLUMNS = [
  { key: 'saved', label: 'Saved', color: 'bg-gray-500' },
  { key: 'applied', label: 'Applied', color: 'bg-blue-500' },
  { key: 'interviewing', label: 'Interviewing', color: 'bg-yellow-500' },
  { key: 'offered', label: 'Offered', color: 'bg-green-500' },
  { key: 'rejected', label: 'Rejected', color: 'bg-red-500' },
];

function Tracker() {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const profiles = await listProfiles();
        if (profiles.length > 0) {
          setUserId(profiles[0].id);
          const [jobsList, statsData] = await Promise.all([
            listSavedJobs(profiles[0].id),
            getJobStats(profiles[0].id),
          ]);
          setJobs(jobsList);
          setStats(statsData);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleStatusChange(jobId, newStatus) {
    try {
      const data = { status: newStatus };
      if (newStatus === 'applied') {
        data.applied_date = new Date().toISOString().split('T')[0];
      }
      await updateSavedJob(jobId, data);
      setJobs(prev => prev.map(j => j.id === jobId ? { ...j, status: newStatus, ...(newStatus === 'applied' ? { applied_date: data.applied_date } : {}) } : j));
      setStats(prev => prev ? { ...prev } : null);
      if (userId) {
        const newStats = await getJobStats(userId);
        setStats(newStats);
      }
      toast.success(`Status updated to ${newStatus}`);
    } catch (err) {
      toast.error('Failed to update status');
    }
  }

  async function handleDelete(jobId) {
    if (!confirm('Delete this saved job?')) return;
    try {
      await deleteSavedJob(jobId);
      setJobs(prev => prev.filter(j => j.id !== jobId));
      if (userId) {
        const newStats = await getJobStats(userId);
        setStats(newStats);
      }
      toast.success('Job deleted');
    } catch (err) {
      toast.error('Failed to delete job');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!userId) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No Profile Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">Create your profile first to start tracking jobs.</p>
        <a href="/profile" className="inline-flex px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium">Create Profile</a>
      </div>
    );
  }

  const jobsByStatus = {};
  COLUMNS.forEach(c => { jobsByStatus[c.key] = []; });
  jobs.forEach(j => {
    if (jobsByStatus[j.status]) jobsByStatus[j.status].push(j);
    else jobsByStatus.saved.push(j);
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Job Tracker</h1>
        <button
          onClick={() => navigate('/tailor')}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium text-sm transition-colors"
        >
          + Add from Tailor
        </button>
      </div>

      {/* Funnel stats */}
      {stats && (
        <div className="grid grid-cols-5 gap-3">
          {COLUMNS.map(col => (
            <div key={col.key} className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-3 text-center">
              <div className={`w-2 h-2 rounded-full ${col.color} mx-auto mb-1`}></div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats[col.key] || 0}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 capitalize">{col.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Kanban board */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {COLUMNS.map(col => (
          <div key={col.key} className="space-y-3">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${col.color}`}></div>
              <h2 className="text-sm font-semibold text-gray-900 dark:text-white uppercase">{col.label}</h2>
              <span className="text-xs text-gray-400 ml-auto">{jobsByStatus[col.key].length}</span>
            </div>
            <div className="space-y-2 min-h-[100px]">
              {jobsByStatus[col.key].map(job => (
                <JobCard
                  key={job.id}
                  job={job}
                  onStatusChange={handleStatusChange}
                  onDelete={handleDelete}
                  onViewDetails={setSelectedJob}
                />
              ))}
              {jobsByStatus[col.key].length === 0 && (
                <div className="border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-lg p-4 text-center text-sm text-gray-400">
                  No jobs
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Detail modal */}
      {selectedJob && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedJob(null)}>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{selectedJob.job_title}</h2>
                <p className="text-gray-600 dark:text-gray-400">{selectedJob.company_name}</p>
              </div>
              <button onClick={() => setSelectedJob(null)} className="text-gray-400 hover:text-gray-600 text-xl">&times;</button>
            </div>

            {selectedJob.quick_score != null && (
              <div className="mb-4">
                <span className="text-sm text-gray-500">Match Score: </span>
                <span className={`font-bold ${selectedJob.quick_score >= 70 ? 'text-green-600' : selectedJob.quick_score >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                  {Math.round(selectedJob.quick_score)}%
                </span>
              </div>
            )}

            {selectedJob.job_url && (
              <p className="text-sm mb-3">
                <a href={selectedJob.job_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">View Job Posting</a>
              </p>
            )}

            {selectedJob.notes && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Notes</h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">{selectedJob.notes}</p>
              </div>
            )}

            {selectedJob.parsed_job_data && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Parsed Job Data</h3>
                {selectedJob.parsed_job_data.required_skills?.length > 0 && (
                  <div className="mb-2">
                    <span className="text-xs text-gray-500">Required Skills: </span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedJob.parsed_job_data.required_skills.map((s, i) => (
                        <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {selectedJob.tailored_resume_ids?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Tailored Resumes</h3>
                <div className="flex gap-2">
                  {selectedJob.tailored_resume_ids.map(id => (
                    <button key={id} onClick={() => { setSelectedJob(null); navigate(`/results/${id}`); }} className="text-sm text-primary-600 hover:underline">
                      Resume #{id}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => { setSelectedJob(null); navigate('/tailor'); }}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm font-medium"
              >
                Tailor Resume for This Job
              </button>
              <button onClick={() => setSelectedJob(null)} className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg text-sm font-medium">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Tracker;
