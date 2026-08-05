import { useState, useEffect } from 'react';
import { Link, useNavigate } from '../router';
import toast from 'react-hot-toast';
import ScoreGauge from '../components/ScoreGauge';
import { listProfiles, generateResume, parseJobDescription, getQuickScore, saveJob } from '../api/client';

function Tailor() {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [parsing, setParsing] = useState(false);
  const [parsedJob, setParsedJob] = useState(null);
  const [step, setStep] = useState(1); // 1: paste JD, 2: review parsed + quick score, 3: generating
  const [quickScore, setQuickScore] = useState(null);
  const [scoring, setScoring] = useState(false);
  const [savingToTracker, setSavingToTracker] = useState(false);
  const [savedJobId, setSavedJobId] = useState(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileError, setProfileError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const profiles = await listProfiles();
        if (profiles.length > 0) setUserId(profiles[0].id);
      } catch (err) {
        setProfileError(err.message || 'Could not load your profile.');
      } finally {
        setProfileLoading(false);
      }
    }
    load();
  }, []);

  async function handleParse() {
    if (!jobDescription.trim()) {
      toast.error('Please paste a job description');
      return;
    }
    setParsing(true);
    try {
      const result = await parseJobDescription(jobDescription);
      setParsedJob(result);
      setStep(2);
      toast.success('Job description parsed');

      // Auto-trigger quick score
      setScoring(true);
      try {
        const scoreResult = await getQuickScore(userId, jobDescription);
        setQuickScore(scoreResult);
      } catch {
        // Score is optional — don't block the flow
      } finally {
        setScoring(false);
      }
    } catch (err) {
      toast.error(`Failed to parse: ${err.message}`);
    } finally {
      setParsing(false);
    }
  }

  async function handleSaveToTracker() {
    setSavingToTracker(true);
    try {
      const result = await saveJob({
        user_id: userId,
        job_title: parsedJob?.job_title || 'Untitled Job',
        company_name: parsedJob?.company_name,
        job_description_text: jobDescription,
      });
      setSavedJobId(result.id);
      toast.success('Job saved to tracker!');
    } catch (err) {
      toast.error(`Failed to save: ${err.message}`);
    } finally {
      setSavingToTracker(false);
    }
  }

  async function handleGenerate() {
    setStep(3);
    try {
      const result = await generateResume(userId, jobDescription, parsedJob, savedJobId);
      toast.success('Resume generated!');
      navigate(`/results/${result.resume_id}`);
    } catch (err) {
      toast.error(`Failed to generate: ${err.message}`);
      setStep(2);
    }
  }

  if (profileLoading) {
    return <div className="flex h-64 items-center justify-center" role="status"><div className="h-8 w-8 animate-spin rounded-full border-2 border-primary-100 border-b-primary-600" /><span className="sr-only">Loading profile</span></div>;
  }

  if (profileError) {
    return <div className="surface-card p-8 text-center" role="alert"><h1 className="text-xl font-bold">Couldn’t load your profile</h1><p className="mt-2 text-slate-600 dark:text-slate-300">{profileError}</p></div>;
  }

  if (!userId) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No Profile Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          You need to create your master profile before tailoring a resume.
        </p>
        <Link to="/profile" className="inline-flex px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium">
          Create Profile
        </Link>
      </div>
    );
  }

  const inputClass = "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tailor Your Resume</h1>

      {/* Step indicator */}
      <ol className="flex items-center gap-2 overflow-x-auto pb-1 sm:gap-4" aria-label="Tailoring progress">
        {[
          { num: 1, label: 'Paste JD' },
          { num: 2, label: 'Review & Score' },
          { num: 3, label: 'Generate' },
        ].map(({ num, label }) => (
          <li key={num} className="flex shrink-0 items-center gap-2" aria-current={step === num ? 'step' : undefined}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
              step >= num ? 'bg-primary-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400'
            }`}>
              {step > num ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
              ) : num}
            </div>
            <span className={`text-sm font-medium ${step >= num ? 'text-gray-900 dark:text-white' : 'text-gray-400'}`}>{label}</span>
            {num < 3 && <div aria-hidden="true" className={`w-4 h-0.5 sm:w-8 ${step > num ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'}`} />}
          </li>
        ))}
      </ol>

      {/* Step 1: Paste Job Description */}
      {step === 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <div>
            <label htmlFor="job-description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Paste the full job description below
            </label>
            <textarea
              id="job-description"
              className={inputClass}
              rows={15}
              value={jobDescription}
              onChange={e => setJobDescription(e.target.value)}
              placeholder="Copy and paste the complete job posting here..."
              maxLength={50000}
              aria-describedby="job-description-help"
            />
            <div id="job-description-help" className="mt-2 flex justify-between gap-4 text-xs text-slate-500 dark:text-slate-400">
              <span>Include responsibilities and requirements for a more useful score.</span>
              <span>{jobDescription.length.toLocaleString()} / 50,000</span>
            </div>
          </div>
          <button
            onClick={handleParse}
            disabled={parsing || !jobDescription.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium transition-colors"
          >
            {parsing ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Parsing...
              </span>
            ) : 'Parse Job Description'}
          </button>
        </div>
      )}

      {/* Step 2: Review Parsed Data + Quick Score */}
      {step === 2 && parsedJob && (
        <div className="space-y-4">
          {/* Quick Score Card */}
          {(scoring || quickScore) && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              {scoring ? (
                <div className="flex items-center gap-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                  <span className="text-gray-600 dark:text-gray-400">Calculating match score...</span>
                </div>
              ) : quickScore && (
                <div className="flex items-center gap-6">
                  <ScoreGauge score={quickScore.overall_score} />
                  <div className="flex-1">
                    <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Quick Match Score</h2>
                    <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">{quickScore.verdict}</p>
                    {quickScore.breakdown?.hard_skills && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {(quickScore.breakdown.hard_skills.matched || []).slice(0, 5).map((s, i) => (
                          <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded text-xs">{s}</span>
                        ))}
                        {(quickScore.breakdown.hard_skills.missing || []).slice(0, 5).map((s, i) => (
                          <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs">{s}</span>
                        ))}
                      </div>
                    )}
                    {quickScore.overall_score < 40 && (
                      <p className="text-sm text-orange-600 dark:text-orange-400 mt-2">
                        Low match — consider upskilling or looking at more aligned roles.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Parsed Job Description</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Job Title</span>
                <p className="text-gray-900 dark:text-white font-medium">{parsedJob.job_title || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Company</span>
                <p className="text-gray-900 dark:text-white font-medium">{parsedJob.company_name || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Seniority</span>
                <p className="text-gray-900 dark:text-white font-medium capitalize">{parsedJob.seniority_level || 'N/A'}</p>
              </div>
              <div>
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Experience Required</span>
                <p className="text-gray-900 dark:text-white font-medium">{parsedJob.years_experience || 'Not specified'}</p>
              </div>
            </div>

            {parsedJob.required_skills?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Required Skills</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {parsedJob.required_skills.map((s, i) => (
                    <span key={i} className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs font-medium">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.preferred_skills?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Preferred Skills</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {parsedJob.preferred_skills.map((s, i) => (
                    <span key={i} className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded text-xs font-medium">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.ats_keywords?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">ATS Keywords</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {parsedJob.ats_keywords.map((k, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded text-xs font-medium">{k}</span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.key_responsibilities?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Key Responsibilities</span>
                <ul className="mt-1 space-y-1">
                  {parsedJob.key_responsibilities.map((r, i) => (
                    <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex"><span className="mr-2">&bull;</span>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => { setStep(1); setQuickScore(null); setSavedJobId(null); }}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-medium"
            >
              Back
            </button>
            <button
              onClick={handleGenerate}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium transition-colors"
            >
              {quickScore ? `Score: ${Math.round(quickScore.overall_score)}% — Generate Tailored Resume` : 'Generate Tailored Resume'}
            </button>
            {!savedJobId ? (
              <button
                onClick={handleSaveToTracker}
                disabled={savingToTracker}
                className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 font-medium border border-gray-300 dark:border-gray-600 text-sm"
              >
                {savingToTracker ? 'Saving...' : 'Save to Tracker'}
              </button>
            ) : (
              <span className="px-4 py-2 text-green-600 dark:text-green-400 text-sm font-medium flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Saved to Tracker
              </span>
            )}
          </div>
        </div>
      )}

      {/* Step 3: Generating */}
      {step === 3 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Generating Your Tailored Resume</h2>
          <p className="text-gray-600 dark:text-gray-400">
            The configured AI provider is comparing your saved profile with the job description and drafting
            an ATS-oriented resume from your existing qualifications.
          </p>
        </div>
      )}
    </div>
  );
}

export default Tailor;
