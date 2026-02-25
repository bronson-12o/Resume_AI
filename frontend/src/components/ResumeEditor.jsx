import { useState } from 'react';

function ResumeEditor({ resumeContent, onSave, onRegenerateSection, saving, regenerating }) {
  const [content, setContent] = useState(resumeContent || {});
  const [hiddenSections, setHiddenSections] = useState(new Set());
  const [editingBullet, setEditingBullet] = useState(null); // {section, jobIdx, bulletIdx}

  const toggleSection = (section) => {
    setHiddenSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) next.delete(section);
      else next.add(section);
      return next;
    });
  };

  const updateBullet = (section, jobIdx, bulletIdx, value) => {
    setContent(prev => {
      const updated = { ...prev };
      if (section === 'work_experience' || section === 'projects') {
        const items = [...(updated[section] || [])];
        const item = { ...items[jobIdx] };
        const bullets = [...(item.bullets || [])];
        bullets[bulletIdx] = value;
        item.bullets = bullets;
        items[jobIdx] = item;
        updated[section] = items;
      }
      return updated;
    });
  };

  const updateSummary = (value) => {
    setContent(prev => ({ ...prev, professional_summary: value }));
  };

  const handleSave = () => {
    // Filter out hidden sections
    const filtered = { ...content };
    hiddenSections.forEach(section => {
      delete filtered[section];
    });
    onSave(filtered);
  };

  const sectionHeader = (title, key) => (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={!hiddenSections.has(key)}
            onChange={() => toggleSection(key)}
            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wide">{title}</h3>
        </label>
      </div>
      <button
        onClick={() => onRegenerateSection(key)}
        disabled={regenerating}
        className="text-xs px-2 py-1 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded border border-primary-200 dark:border-primary-800"
      >
        {regenerating ? 'Regenerating...' : 'Regenerate'}
      </button>
    </div>
  );

  return (
    <div className="space-y-4">
      {/* Summary */}
      {content.professional_summary !== undefined && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('professional_summary') ? 'opacity-50' : ''}`}>
          {sectionHeader('Professional Summary', 'professional_summary')}
          {!hiddenSections.has('professional_summary') && (
            <textarea
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
              rows={3}
              value={content.professional_summary || ''}
              onChange={e => updateSummary(e.target.value)}
            />
          )}
        </div>
      )}

      {/* Work Experience */}
      {content.work_experience?.length > 0 && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('work_experience') ? 'opacity-50' : ''}`}>
          {sectionHeader('Work Experience', 'work_experience')}
          {!hiddenSections.has('work_experience') && content.work_experience.map((job, jobIdx) => (
            <div key={jobIdx} className="mb-4 last:mb-0">
              <div className="flex justify-between items-baseline mb-1">
                <span className="font-medium text-gray-900 dark:text-white text-sm">
                  {job.title} | <em className="text-gray-600 dark:text-gray-400">{job.company}</em>
                </span>
                <span className="text-xs text-gray-500">{job.dates}</span>
              </div>
              <ul className="space-y-1">
                {(job.bullets || []).map((bullet, bulletIdx) => (
                  <li key={bulletIdx} className="flex items-start gap-1">
                    <span className="text-gray-400 mt-0.5 text-xs">•</span>
                    {editingBullet?.section === 'work_experience' && editingBullet?.jobIdx === jobIdx && editingBullet?.bulletIdx === bulletIdx ? (
                      <input
                        autoFocus
                        className="flex-1 px-2 py-0.5 border border-primary-300 dark:border-primary-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        value={bullet}
                        onChange={e => updateBullet('work_experience', jobIdx, bulletIdx, e.target.value)}
                        onBlur={() => setEditingBullet(null)}
                        onKeyDown={e => e.key === 'Enter' && setEditingBullet(null)}
                      />
                    ) : (
                      <span
                        className="flex-1 text-sm text-gray-600 dark:text-gray-400 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 rounded px-1"
                        onClick={() => setEditingBullet({ section: 'work_experience', jobIdx, bulletIdx })}
                      >
                        {bullet}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {/* Skills */}
      {content.skills && Object.keys(content.skills).length > 0 && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('skills') ? 'opacity-50' : ''}`}>
          {sectionHeader('Technical Skills', 'skills')}
          {!hiddenSections.has('skills') && Object.entries(content.skills).map(([category, skillList]) => (
            <div key={category} className="mb-2">
              <span className="text-sm font-medium text-gray-900 dark:text-white">{category}: </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">{(skillList || []).join(', ')}</span>
            </div>
          ))}
        </div>
      )}

      {/* Projects */}
      {content.projects?.length > 0 && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('projects') ? 'opacity-50' : ''}`}>
          {sectionHeader('Projects', 'projects')}
          {!hiddenSections.has('projects') && content.projects.map((project, projIdx) => (
            <div key={projIdx} className="mb-3 last:mb-0">
              <div className="font-medium text-sm text-gray-900 dark:text-white">
                {project.name}
                {project.technologies?.length > 0 && (
                  <span className="text-gray-500 font-normal"> | {project.technologies.join(', ')}</span>
                )}
              </div>
              <ul className="space-y-1 mt-1">
                {(project.bullets || []).map((bullet, bulletIdx) => (
                  <li key={bulletIdx} className="flex items-start gap-1">
                    <span className="text-gray-400 mt-0.5 text-xs">•</span>
                    {editingBullet?.section === 'projects' && editingBullet?.jobIdx === projIdx && editingBullet?.bulletIdx === bulletIdx ? (
                      <input
                        autoFocus
                        className="flex-1 px-2 py-0.5 border border-primary-300 dark:border-primary-600 rounded text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        value={bullet}
                        onChange={e => updateBullet('projects', projIdx, bulletIdx, e.target.value)}
                        onBlur={() => setEditingBullet(null)}
                        onKeyDown={e => e.key === 'Enter' && setEditingBullet(null)}
                      />
                    ) : (
                      <span
                        className="flex-1 text-sm text-gray-600 dark:text-gray-400 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 rounded px-1"
                        onClick={() => setEditingBullet({ section: 'projects', jobIdx: projIdx, bulletIdx })}
                      >
                        {bullet}
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}

      {/* Education */}
      {content.education?.length > 0 && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('education') ? 'opacity-50' : ''}`}>
          {sectionHeader('Education', 'education')}
          {!hiddenSections.has('education') && content.education.map((edu, i) => (
            <div key={i} className="mb-2">
              <span className="font-medium text-sm text-gray-900 dark:text-white">{edu.degree}</span>
              <span className="text-sm text-gray-600 dark:text-gray-400"> | {edu.institution}</span>
              {edu.graduation_date && <span className="text-sm text-gray-500"> | {edu.graduation_date}</span>}
            </div>
          ))}
        </div>
      )}

      {/* Certifications */}
      {content.certifications?.length > 0 && (
        <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 ${hiddenSections.has('certifications') ? 'opacity-50' : ''}`}>
          {sectionHeader('Certifications', 'certifications')}
          {!hiddenSections.has('certifications') && content.certifications.map((cert, i) => (
            <div key={i} className="text-sm text-gray-700 dark:text-gray-300 mb-1">
              <strong>{cert.name}</strong> — {cert.issuing_org} {cert.date && `(${cert.date})`}
            </div>
          ))}
        </div>
      )}

      {/* Save button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium transition-colors"
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}

export default ResumeEditor;
