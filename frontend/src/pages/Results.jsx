import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import ScoreGauge from '../components/ScoreGauge';
import ResumePreview from '../components/ResumePreview';
import GapCard from '../components/GapCard';
import { getResume, downloadResume, getSectorSuggestions, listProfiles } from '../api/client';

function Results() {
  const { resumeId } = useParams();
  const [resume, setResume] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState('preview'); // preview, score, recommendations, sectors
  const [sectors, setSectors] = useState(null);
  const [loadingSectors, setLoadingSectors] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await getResume(resumeId);
        setResume(data);
      } catch (err) {
        toast.error('Failed to load resume');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [resumeId]);

  async function handleDownload() {
    try {
      await downloadResume(resumeId);
      toast.success('Download started');
    } catch (err) {
      toast.error('Download failed');
    }
  }

  async function handleExploreSectors() {
    if (sectors) return;
    setLoadingSectors(true);
    try {
      const profiles = await listProfiles();
      if (profiles.length > 0) {
        const result = await getSectorSuggestions(profiles[0].id);
        setSectors(result);
      }
    } catch (err) {
      toast.error('Failed to load sector suggestions');
    } finally {
      setLoadingSectors(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!resume) {
    return <p className="text-gray-500">Resume not found.</p>;
  }

  const score = resume.match_score;
  const recs = resume.recommendations;

  const sectionBtnClass = (section) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      activeSection === section
        ? 'bg-primary-600 text-white'
        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
    }`;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {resume.job_title_applied || 'Tailored Resume'}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {resume.company_name || 'Unknown company'} &middot; Generated {resume.created_at ? new Date(resume.created_at).toLocaleDateString() : ''}
          </p>
        </div>
        <button
          onClick={handleDownload}
          className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download .docx
        </button>
      </div>

      {/* Section Tabs */}
      <div className="flex flex-wrap gap-2">
        <button onClick={() => setActiveSection('preview')} className={sectionBtnClass('preview')}>Resume Preview</button>
        <button onClick={() => setActiveSection('score')} className={sectionBtnClass('score')}>Match Score</button>
        <button onClick={() => setActiveSection('recommendations')} className={sectionBtnClass('recommendations')}>Recommendations</button>
        <button onClick={() => { setActiveSection('sectors'); handleExploreSectors(); }} className={sectionBtnClass('sectors')}>Sector Explorer</button>
      </div>

      {/* Resume Preview */}
      {activeSection === 'preview' && (
        <ResumePreview html={resume.html_preview} />
      )}

      {/* Match Score */}
      {activeSection === 'score' && score && (
        <div className="space-y-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="flex items-center gap-6 mb-6">
              <ScoreGauge score={typeof score === 'object' ? score.overall_score : score} />
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Overall Match</h2>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  {typeof score === 'object' ? score.verdict : `Match score: ${Math.round(score)}%`}
                </p>
              </div>
            </div>

            {typeof score === 'object' && score.breakdown && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(score.breakdown).map(([key, data]) => (
                  <div key={key} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-gray-900 dark:text-white capitalize">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className={`font-bold ${
                        data.score >= 70 ? 'text-green-600' : data.score >= 50 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {Math.round(data.score)}%
                      </span>
                    </div>
                    {/* Score bar */}
                    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2 mb-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          data.score >= 70 ? 'bg-green-500' : data.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(data.score, 100)}%` }}
                      />
                    </div>
                    {data.matched?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {data.matched.map((m, i) => (
                          <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded text-xs">{m}</span>
                        ))}
                      </div>
                    )}
                    {data.missing?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {data.missing.map((m, i) => (
                          <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs">{m}</span>
                        ))}
                      </div>
                    )}
                    {data.top_missing_keywords?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {data.top_missing_keywords.map((k, i) => (
                          <span key={i} className="px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded text-xs">{k}</span>
                        ))}
                      </div>
                    )}
                    {data.notes && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{data.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Keywords summary */}
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Keyword Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {resume.matched_keywords?.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-green-600 dark:text-green-400">Matched Keywords</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {resume.matched_keywords.map((k, i) => (
                      <span key={i} className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded text-xs">{k}</span>
                    ))}
                  </div>
                </div>
              )}
              {resume.missing_keywords?.length > 0 && (
                <div>
                  <span className="text-sm font-medium text-red-600 dark:text-red-400">Missing Keywords</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {resume.missing_keywords.map((k, i) => (
                      <span key={i} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded text-xs">{k}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {activeSection === 'recommendations' && recs && (
        <div className="space-y-4">
          {recs.general_advice && (
            <div className="bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
              <p className="text-primary-800 dark:text-primary-300 font-medium">{recs.general_advice}</p>
            </div>
          )}

          {recs.skill_recommendations?.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Skill Gap Recommendations</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {recs.skill_recommendations.map((rec, i) => (
                  <GapCard key={i} recommendation={rec} />
                ))}
              </div>
            </div>
          )}

          {recs.keyword_suggestions?.length > 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Keyword Optimization Tips</h3>
              <div className="space-y-3">
                {recs.keyword_suggestions.map((sug, i) => (
                  <div key={i} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400 rounded text-xs font-medium">
                        {sug.missing_keyword}
                      </span>
                      {sug.existing_equivalent && (
                        <>
                          <span className="text-gray-400 text-xs">~</span>
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded text-xs font-medium">
                            {sug.existing_equivalent}
                          </span>
                        </>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{sug.suggestion}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sector Explorer */}
      {activeSection === 'sectors' && (
        <div className="space-y-4">
          {loadingSectors && (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          )}

          {sectors && (
            <>
              {sectors.career_insight && (
                <div className="bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
                  <p className="text-primary-800 dark:text-primary-300 font-medium">{sectors.career_insight}</p>
                </div>
              )}

              {sectors.alternative_titles?.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Alternative Job Titles to Search</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {sectors.alternative_titles.map((title, i) => (
                      <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="font-medium text-gray-900 dark:text-white">{title.title}</div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{title.relevance}</p>
                        {title.search_tip && (
                          <p className="text-xs text-primary-600 dark:text-primary-400 mt-1">{title.search_tip}</p>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {sectors.industry_suggestions?.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Industries to Consider</h3>
                  <div className="space-y-3">
                    {sectors.industry_suggestions.map((ind, i) => (
                      <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="font-medium text-gray-900 dark:text-white">{ind.industry}</div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{ind.explanation}</p>
                        {ind.example_roles?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {ind.example_roles.map((r, j) => (
                              <span key={j} className="px-2 py-0.5 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded text-xs">{r}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}

export default Results;
