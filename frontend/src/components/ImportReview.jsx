import { useState } from 'react';

const inputClass = "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm";
const labelClass = "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1";

function ImportReview({ data, onConfirm, onCancel, saving }) {
  const [form, setForm] = useState({
    name: data.name || '',
    email: data.email || '',
    phone: data.phone || '',
    location: data.location || '',
    linkedin_url: data.linkedin_url || '',
    portfolio_url: data.portfolio_url || '',
    professional_summary: data.professional_summary || '',
    experiences: data.experiences || [],
    education: data.education || [],
    skills: data.skills || [],
    projects: data.projects || [],
    certifications: data.certifications || [],
  });

  return (
    <div className="space-y-6">
      <div className="bg-primary-50 dark:bg-primary-900/20 rounded-xl p-4 border border-primary-200 dark:border-primary-800">
        <p className="text-primary-800 dark:text-primary-300 font-medium">
          Review the parsed data below. Edit any fields before saving to your profile.
        </p>
      </div>

      {/* Personal Info */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Personal Info</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div><label className={labelClass}>Name</label><input className={inputClass} value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} /></div>
          <div><label className={labelClass}>Email</label><input className={inputClass} value={form.email} onChange={e => setForm(p => ({ ...p, email: e.target.value }))} /></div>
          <div><label className={labelClass}>Phone</label><input className={inputClass} value={form.phone} onChange={e => setForm(p => ({ ...p, phone: e.target.value }))} /></div>
          <div><label className={labelClass}>Location</label><input className={inputClass} value={form.location} onChange={e => setForm(p => ({ ...p, location: e.target.value }))} /></div>
        </div>
        <div className="mt-4">
          <label className={labelClass}>Professional Summary</label>
          <textarea className={inputClass} rows={3} value={form.professional_summary} onChange={e => setForm(p => ({ ...p, professional_summary: e.target.value }))} />
        </div>
      </div>

      {/* Experience summary */}
      {form.experiences.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Experience ({form.experiences.length} positions)
          </h3>
          {form.experiences.map((exp, i) => (
            <div key={i} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg mb-2">
              <div className="font-medium text-gray-900 dark:text-white">{exp.job_title}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">{exp.company_name} | {exp.start_date} - {exp.end_date || 'Present'}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">{(exp.bullet_points || []).length} bullet points</div>
            </div>
          ))}
        </div>
      )}

      {/* Education summary */}
      {form.education.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Education ({form.education.length})
          </h3>
          {form.education.map((edu, i) => (
            <div key={i} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg mb-2">
              <div className="font-medium text-gray-900 dark:text-white">{edu.degree}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">{edu.institution}</div>
            </div>
          ))}
        </div>
      )}

      {/* Skills summary */}
      {form.skills.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Skills ({form.skills.length})
          </h3>
          <div className="flex flex-wrap gap-2">
            {form.skills.map((s, i) => (
              <span key={i} className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded text-xs font-medium">
                {s.skill_name} ({s.proficiency_level})
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Projects summary */}
      {form.projects.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-4">
            Projects ({form.projects.length})
          </h3>
          {form.projects.map((p, i) => (
            <div key={i} className="text-sm text-gray-700 dark:text-gray-300 mb-1">{p.project_name}</div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        <button onClick={onCancel} className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 font-medium">
          Cancel
        </button>
        <button
          onClick={() => onConfirm(form)}
          disabled={saving || !form.name || !form.email}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium transition-colors"
        >
          {saving ? 'Saving...' : 'Confirm & Save to Profile'}
        </button>
      </div>
    </div>
  );
}

export default ImportReview;
