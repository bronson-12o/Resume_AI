import { useState, useEffect } from 'react';
import { Link } from '../router';
import { listProfiles, getResumeHistory, getJobStats } from '../api/client';

function Dashboard() {
  const [profiles, setProfiles] = useState([]);
  const [history, setHistory] = useState([]);
  const [jobStats, setJobStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    async function load() {
      setError('');
      setLoading(true);
      try {
        const profileList = await listProfiles();
        setProfiles(profileList);
        if (profileList.length > 0) {
          const [hist, stats] = await Promise.all([
            getResumeHistory(profileList[0].id),
            getJobStats(profileList[0].id).catch(() => null),
          ]);
          setHistory(hist);
          setJobStats(stats);
        }
      } catch (err) {
        setError(err.message || 'The dashboard could not connect to ResumeAI.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [reloadKey]);

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center" role="status">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-100 border-b-primary-600"></div>
        <span className="sr-only">Loading dashboard</span>
      </div>
    );
  }

  if (error) {
    return (
      <section className="surface-card p-8 text-center" role="alert">
        <p className="eyebrow">Connection problem</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-950 dark:text-white">We couldn’t load your workspace</h1>
        <p className="mx-auto mt-2 max-w-lg text-slate-600 dark:text-slate-300">{error} Check that the backend is running, then try again.</p>
        <button className="button-primary mt-6" onClick={() => setReloadKey((key) => key + 1)}>Try again</button>
      </section>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="surface-card overflow-hidden p-6 sm:p-8 lg:p-10">
        <p className="eyebrow">Truthful tailoring, from profile to application</p>
        <h1 className="mt-3 max-w-3xl text-3xl font-bold tracking-tight text-slate-950 dark:text-white sm:text-4xl">
          Build a stronger application from the experience you already have.
        </h1>
        <p className="mb-7 mt-4 max-w-2xl text-base leading-7 text-slate-600 dark:text-slate-300 sm:text-lg">
          Keep one complete career profile, compare it with a role, and create focused materials without inventing qualifications. Your data stays in this installation.
        </p>

        {/* How it works */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
            <div className="text-primary-600 dark:text-primary-400 font-bold text-lg mb-1">1. Build Profile</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Add all your experience, skills, projects, and certifications to your master profile.
            </p>
          </div>
          <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
            <div className="text-primary-600 dark:text-primary-400 font-bold text-lg mb-1">2. Paste Job Description</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Paste the job posting you want to apply for. ResumeAI extracts its requirements and keywords.
            </p>
          </div>
          <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
            <div className="text-primary-600 dark:text-primary-400 font-bold text-lg mb-1">3. Get Tailored Resume</div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Receive an ATS-oriented resume draft, match score, and skill gap recommendations.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          {profiles.length === 0 ? (
            <Link
              to="/profile"
              className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
            >
              Get Started — Create Profile
            </Link>
          ) : (
            <>
              <Link
                to="/tailor"
                className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
              >
                Tailor a Resume
              </Link>
              <Link
                to="/profile"
                className="inline-flex items-center px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-medium rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Edit Profile
              </Link>
            </>
          )}
        </div>
      </div>

      {/* Application Funnel */}
      {jobStats && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Application Pipeline</h2>
            <Link to="/tracker" className="text-sm text-primary-600 hover:underline">View Tracker</Link>
          </div>
          <div className="grid grid-cols-5 gap-3">
            {[
              { key: 'saved', label: 'Saved', color: 'bg-gray-500' },
              { key: 'applied', label: 'Applied', color: 'bg-blue-500' },
              { key: 'interviewing', label: 'Interviewing', color: 'bg-yellow-500' },
              { key: 'offered', label: 'Offered', color: 'bg-green-500' },
              { key: 'rejected', label: 'Rejected', color: 'bg-red-500' },
            ].map(col => (
              <div key={col.key} className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${col.color} mx-auto mb-1`}></div>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">{jobStats[col.key] || 0}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">{col.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Profile Summary */}
      {profiles.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Your Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{profiles[0].name?.split(' ')[0]}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">{profiles[0].email}</div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{profiles[0].location || '—'}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Location</div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">{history.length}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Resumes Generated</div>
            </div>
            <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {history.length > 0 ? `${Math.round(history[0].match_score || 0)}%` : '—'}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">Latest Score</div>
            </div>
          </div>
        </div>
      )}

      {/* Resume History */}
      {history.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Resume History</h2>
          <div className="space-y-3">
            {history.map((resume) => (
              <Link
                key={resume.id}
                to={`/results/${resume.id}`}
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
              >
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">
                    {resume.job_title_applied || 'Untitled'}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {resume.company_name || 'Unknown company'} &middot;{' '}
                    {resume.created_at ? new Date(resume.created_at).toLocaleDateString() : ''}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-lg font-bold ${
                    (resume.match_score || 0) >= 70
                      ? 'text-green-600 dark:text-green-400'
                      : (resume.match_score || 0) >= 50
                      ? 'text-yellow-600 dark:text-yellow-400'
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {Math.round(resume.match_score || 0)}%
                  </span>
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
