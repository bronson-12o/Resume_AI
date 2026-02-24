import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { listProfiles, generateResume, parseJobDescription } from '../api/client';

function Tailor() {
  const navigate = useNavigate();
  const [userId, setUserId] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [parsedJob, setParsedJob] = useState(null);
  const [step, setStep] = useState(1); // 1: paste JD, 2: review parsed, 3: generating

  useEffect(() => {
    async function load() {
      const profiles = await listProfiles();
      if (profiles.length > 0) {
        setUserId(profiles[0].id);
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
    } catch (err) {
      toast.error(`Failed to parse: ${err.message}`);
    } finally {
      setParsing(false);
    }
  }

  async function handleGenerate() {
    setStep(3);
    setLoading(true);
    try {
      const result = await generateResume(userId, jobDescription, parsedJob);
      toast.success('Resume generated!');
      navigate(`/results/${result.resume_id}`);
    } catch (err) {
      toast.error(`Failed to generate: ${err.message}`);
      setStep(2);
    } finally {
      setLoading(false);
    }
  }

  if (!userId) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 text-center">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">No Profile Found</h2>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          You need to create your master profile before tailoring a resume.
        </p>
        <a href="/profile" className="inline-flex px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium">
          Create Profile
        </a>
      </div>
    );
  }

  const inputClass = "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm";

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tailor Your Resume</h1>

      {/* Step indicator */}
      <div className="flex items-center gap-4">
        {[
          { num: 1, label: 'Paste JD' },
          { num: 2, label: 'Review' },
          { num: 3, label: 'Generate' },
        ].map(({ num, label }) => (
          <div key={num} className="flex items-center gap-2">
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
            {num < 3 && <div className={`w-8 h-0.5 ${step > num ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700'}`} />}
          </div>
        ))}
      </div>

      {/* Step 1: Paste Job Description */}
      {step === 1 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Paste the full job description below
            </label>
            <textarea
              className={inputClass}
              rows={15}
              value={jobDescription}
              onChange={e => setJobDescription(e.target.value)}
              placeholder="Copy and paste the complete job posting here..."
            />
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

      {/* Step 2: Review Parsed Data */}
      {step === 2 && parsedJob && (
        <div className="space-y-4">
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
                    <span key={i} className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.preferred_skills?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Preferred Skills</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {parsedJob.preferred_skills.map((s, i) => (
                    <span key={i} className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded text-xs font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.ats_keywords?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">ATS Keywords</span>
                <div className="flex flex-wrap gap-2 mt-1">
                  {parsedJob.ats_keywords.map((k, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded text-xs font-medium">
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {parsedJob.key_responsibilities?.length > 0 && (
              <div className="mt-4">
                <span className="text-sm font-medium text-gray-500 dark:text-gray-400">Key Responsibilities</span>
                <ul className="mt-1 space-y-1">
                  {parsedJob.key_responsibilities.map((r, i) => (
                    <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex"><span className="mr-2">•</span>{r}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep(1)}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-medium"
            >
              Back
            </button>
            <button
              onClick={handleGenerate}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium transition-colors"
            >
              Generate Tailored Resume
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Generating */}
      {step === 3 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-12 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Generating Your Tailored Resume</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Our AI is analyzing your profile against the job description, optimizing for ATS compatibility,
            and tailoring your experience to highlight the most relevant qualifications.
          </p>
        </div>
      )}
    </div>
  );
}

export default Tailor;
