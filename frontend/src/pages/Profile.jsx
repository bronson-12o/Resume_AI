import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import ProfileForm from '../components/ProfileForm';
import SkillTag from '../components/SkillTag';
import ImportReview from '../components/ImportReview';
import ConfirmDialog from '../components/ConfirmDialog';
import {
  listProfiles, createProfile, updateProfile, getProfile,
  addExperience, updateExperience, deleteExperience,
  addEducation, updateEducation, deleteEducation,
  addSkill, deleteSkill,
  addProject, updateProject, deleteProject,
  addCertification, updateCertification, deleteCertification,
  importResume, confirmImport,
} from '../api/client';

const TABS = ['Personal Info', 'Experience', 'Education', 'Skills', 'Projects', 'Certifications'];

function Profile() {
  const [activeTab, setActiveTab] = useState(0);
  const [userId, setUserId] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form states
  const [userForm, setUserForm] = useState({
    name: '', email: '', phone: '', location: '',
    linkedin_url: '', portfolio_url: '', professional_summary: '',
  });
  const [expForm, setExpForm] = useState({
    job_title: '', company_name: '', location: '', start_date: '',
    end_date: '', bullet_points: [''], skills_used: [''], is_current: false,
  });
  const [editingExpId, setEditingExpId] = useState(null);
  const [eduForm, setEduForm] = useState({
    degree: '', institution: '', graduation_date: '', gpa: '', relevant_coursework: [''],
  });
  const [editingEduId, setEditingEduId] = useState(null);
  const [skillForm, setSkillForm] = useState({
    skill_name: '', category: 'programming', proficiency_level: 'intermediate',
  });
  const [projForm, setProjForm] = useState({
    project_name: '', description: '', technologies_used: [''], url: '', bullet_points: [''],
  });
  const [editingProjId, setEditingProjId] = useState(null);
  const [certForm, setCertForm] = useState({
    cert_name: '', issuing_org: '', date_obtained: '', expiry_date: '', credential_url: '',
  });
  const [editingCertId, setEditingCertId] = useState(null);
  const [importMode, setImportMode] = useState(false);
  const [importData, setImportData] = useState(null);
  const [importing, setImporting] = useState(false);
  const [loadError, setLoadError] = useState('');
  const [pendingDelete, setPendingDelete] = useState(null);

  async function handleFileUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true);
    try {
      const parsed = await importResume(file);
      setImportData(parsed);
      setImportMode(true);
      toast.success('Resume parsed successfully! Review the data below.');
    } catch (err) {
      toast.error(`Import failed: ${err.message}`);
    } finally {
      setImporting(false);
    }
  }

  async function handleConfirmImport(data) {
    setSaving(true);
    try {
      if (!userId) {
        const created = await createProfile({ name: data.name, email: data.email, phone: data.phone, location: data.location, linkedin_url: data.linkedin_url, portfolio_url: data.portfolio_url, professional_summary: data.professional_summary });
        setUserId(created.id);
        await confirmImport(created.id, data);
      } else {
        await confirmImport(userId, data);
      }
      toast.success('Profile updated from resume!');
      setImportMode(false);
      setImportData(null);
      await loadProfile();
    } catch (err) {
      toast.error(`Save failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => { loadProfile(); }, []);

  async function loadProfile() {
    setLoadError('');
    try {
      const profiles = await listProfiles();
      if (profiles.length > 0) {
        setUserId(profiles[0].id);
        const full = await getProfile(profiles[0].id);
        setProfile(full);
        setUserForm({
          name: full.user.name || '',
          email: full.user.email || '',
          phone: full.user.phone || '',
          location: full.user.location || '',
          linkedin_url: full.user.linkedin_url || '',
          portfolio_url: full.user.portfolio_url || '',
          professional_summary: full.user.professional_summary || '',
        });
      }
    } catch (err) {
      setLoadError(err.message || 'Could not load your profile.');
    } finally {
      setLoading(false);
    }
  }

  async function reload() {
    if (userId) {
      const full = await getProfile(userId);
      setProfile(full);
    }
  }

  // --- Personal Info ---
  async function handleSaveUser(e) {
    e.preventDefault();
    setSaving(true);
    try {
      if (userId) {
        await updateProfile(userId, userForm);
        toast.success('Profile updated');
      } else {
        const created = await createProfile(userForm);
        setUserId(created.id);
        toast.success('Profile created');
      }
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  // --- Experience ---
  async function handleSaveExp(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...expForm,
        bullet_points: expForm.bullet_points.filter(b => b.trim()),
        skills_used: expForm.skills_used.filter(s => s.trim()),
      };
      if (editingExpId) {
        await updateExperience(userId, editingExpId, data);
        toast.success('Experience updated');
        setEditingExpId(null);
      } else {
        await addExperience(userId, data);
        toast.success('Experience added');
      }
      resetExpForm();
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  function resetExpForm() {
    setExpForm({ job_title: '', company_name: '', location: '', start_date: '', end_date: '', bullet_points: [''], skills_used: [''], is_current: false });
    setEditingExpId(null);
  }

  function handleDeleteExp(expId) {
    setPendingDelete({ type: 'experience', id: expId, label: 'experience' });
  }

  function editExp(exp) {
    setEditingExpId(exp.id);
    setExpForm({
      job_title: exp.job_title,
      company_name: exp.company_name,
      location: exp.location || '',
      start_date: exp.start_date,
      end_date: exp.end_date || '',
      bullet_points: exp.bullet_points?.length ? exp.bullet_points : [''],
      skills_used: exp.skills_used?.length ? exp.skills_used : [''],
      is_current: exp.is_current,
    });
  }

  // --- Education ---
  async function handleSaveEdu(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const data = { ...eduForm, relevant_coursework: eduForm.relevant_coursework.filter(c => c.trim()) };
      if (editingEduId) {
        await updateEducation(userId, editingEduId, data);
        toast.success('Education updated');
        setEditingEduId(null);
      } else {
        await addEducation(userId, data);
        toast.success('Education added');
      }
      setEduForm({ degree: '', institution: '', graduation_date: '', gpa: '', relevant_coursework: [''] });
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleDeleteEdu(eduId) {
    setPendingDelete({ type: 'education', id: eduId, label: 'education entry' });
  }

  function editEdu(edu) {
    setEditingEduId(edu.id);
    setEduForm({
      degree: edu.degree,
      institution: edu.institution,
      graduation_date: edu.graduation_date || '',
      gpa: edu.gpa || '',
      relevant_coursework: edu.relevant_coursework?.length ? edu.relevant_coursework : [''],
    });
  }

  // --- Skills ---
  async function handleAddSkill(e) {
    e.preventDefault();
    if (!skillForm.skill_name.trim()) return;
    setSaving(true);
    try {
      await addSkill(userId, skillForm);
      toast.success('Skill added');
      setSkillForm({ skill_name: '', category: 'programming', proficiency_level: 'intermediate' });
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleDeleteSkill(skillId) {
    setPendingDelete({ type: 'skill', id: skillId, label: 'skill' });
  }

  // --- Projects ---
  async function handleSaveProj(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const data = {
        ...projForm,
        technologies_used: projForm.technologies_used.filter(t => t.trim()),
        bullet_points: projForm.bullet_points.filter(b => b.trim()),
      };
      if (editingProjId) {
        await updateProject(userId, editingProjId, data);
        toast.success('Project updated');
        setEditingProjId(null);
      } else {
        await addProject(userId, data);
        toast.success('Project added');
      }
      setProjForm({ project_name: '', description: '', technologies_used: [''], url: '', bullet_points: [''] });
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleDeleteProj(projId) {
    setPendingDelete({ type: 'project', id: projId, label: 'project' });
  }

  function editProj(proj) {
    setEditingProjId(proj.id);
    setProjForm({
      project_name: proj.project_name,
      description: proj.description || '',
      technologies_used: proj.technologies_used?.length ? proj.technologies_used : [''],
      url: proj.url || '',
      bullet_points: proj.bullet_points?.length ? proj.bullet_points : [''],
    });
  }

  // --- Certifications ---
  async function handleSaveCert(e) {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingCertId) {
        await updateCertification(userId, editingCertId, certForm);
        toast.success('Certification updated');
        setEditingCertId(null);
      } else {
        await addCertification(userId, certForm);
        toast.success('Certification added');
      }
      setCertForm({ cert_name: '', issuing_org: '', date_obtained: '', expiry_date: '', credential_url: '' });
      await reload();
    } catch (err) {
      toast.error(err.message);
    } finally {
      setSaving(false);
    }
  }

  function handleDeleteCert(certId) {
    setPendingDelete({ type: 'certification', id: certId, label: 'certification' });
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setSaving(true);
    try {
      const actions = {
        experience: deleteExperience,
        education: deleteEducation,
        skill: deleteSkill,
        project: deleteProject,
        certification: deleteCertification,
      };
      await actions[pendingDelete.type](userId, pendingDelete.id);
      toast.success(`${pendingDelete.label[0].toUpperCase()}${pendingDelete.label.slice(1)} deleted`);
      setPendingDelete(null);
      await reload();
    } catch (err) {
      toast.error(`Delete failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  }

  function editCert(cert) {
    setEditingCertId(cert.id);
    setCertForm({
      cert_name: cert.cert_name,
      issuing_org: cert.issuing_org || '',
      date_obtained: cert.date_obtained || '',
      expiry_date: cert.expiry_date || '',
      credential_url: cert.credential_url || '',
    });
  }

  // --- Dynamic array field helpers ---
  function updateArrayField(setter, field, index, value) {
    setter(prev => {
      const arr = [...prev[field]];
      arr[index] = value;
      return { ...prev, [field]: arr };
    });
  }

  function addArrayItem(setter, field) {
    setter(prev => ({ ...prev, [field]: [...prev[field], ''] }));
  }

  function removeArrayItem(setter, field, index) {
    setter(prev => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="surface-card p-8 text-center" role="alert">
        <h1 className="text-xl font-bold">Couldn’t load your profile</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">{loadError}</p>
        <button className="button-primary mt-5" onClick={loadProfile}>Try again</button>
      </div>
    );
  }

  const inputClass = "w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm";
  const labelClass = "block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1";
  const btnPrimary = "px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors text-sm font-medium";
  const btnSecondary = "px-3 py-1.5 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors text-sm";
  const btnDanger = "px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors text-sm";

  if (importMode && importData) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Review Imported Resume</h1>
        <ImportReview
          data={importData}
          onConfirm={handleConfirmImport}
          onCancel={() => { setImportMode(false); setImportData(null); }}
          saving={saving}
        />
      </div>
    );
  }

  return (
    <>
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Master Profile</h1>
        <label className={`${importing ? 'opacity-50 cursor-wait' : 'cursor-pointer'} inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium text-sm transition-colors`}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          {importing ? 'Parsing...' : 'Import Resume'}
          <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} className="hidden" disabled={importing} />
        </label>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1" role="tablist" aria-label="Profile sections">
        {TABS.map((tab, i) => (
          <button
            key={tab}
            onClick={() => setActiveTab(i)}
            role="tab"
            aria-selected={activeTab === i}
            aria-controls={`profile-panel-${i}`}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === i
                ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      <div id={`profile-panel-${activeTab}`} className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6" role="tabpanel">
        {/* TAB 0: Personal Info */}
        {activeTab === 0 && (
          <form onSubmit={handleSaveUser} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ProfileForm label="Full Name *" value={userForm.name} onChange={v => setUserForm(p => ({ ...p, name: v }))} required />
              <ProfileForm label="Email *" type="email" value={userForm.email} onChange={v => setUserForm(p => ({ ...p, email: v }))} required />
              <ProfileForm label="Phone" value={userForm.phone} onChange={v => setUserForm(p => ({ ...p, phone: v }))} />
              <ProfileForm label="Location" value={userForm.location} onChange={v => setUserForm(p => ({ ...p, location: v }))} placeholder="City, State" />
              <ProfileForm label="LinkedIn URL" value={userForm.linkedin_url} onChange={v => setUserForm(p => ({ ...p, linkedin_url: v }))} />
              <ProfileForm label="Portfolio URL" value={userForm.portfolio_url} onChange={v => setUserForm(p => ({ ...p, portfolio_url: v }))} />
            </div>
            <div>
              <label htmlFor="professional-summary" className={labelClass}>Professional Summary</label>
              <textarea
                id="professional-summary"
                className={inputClass}
                rows={4}
                value={userForm.professional_summary}
                onChange={e => setUserForm(p => ({ ...p, professional_summary: e.target.value }))}
                placeholder="A general summary of your professional background that can be adapted for different roles..."
              />
            </div>
            <button type="submit" className={btnPrimary} disabled={saving}>
              {saving ? 'Saving...' : userId ? 'Update Profile' : 'Create Profile'}
            </button>
          </form>
        )}

        {/* TAB 1: Experience */}
        {activeTab === 1 && (
          <div className="space-y-6">
            {!userId && <p className="text-gray-500">Create your profile first in the Personal Info tab.</p>}
            {userId && (
              <>
                {/* Existing experiences */}
                {profile?.experiences?.map(exp => (
                  <div key={exp.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-medium text-gray-900 dark:text-white">{exp.job_title}</div>
                        <div className="text-sm text-gray-600 dark:text-gray-400">{exp.company_name} | {exp.start_date} - {exp.end_date || 'Present'}</div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => editExp(exp)} className={btnSecondary}>Edit</button>
                        <button onClick={() => handleDeleteExp(exp.id)} className={btnDanger}>Delete</button>
                      </div>
                    </div>
                    {exp.bullet_points?.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {exp.bullet_points.map((b, i) => (
                          <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex"><span className="mr-2">•</span>{b}</li>
                        ))}
                      </ul>
                    )}
                    {exp.skills_used?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {exp.skills_used.map((s, i) => <SkillTag key={i} name={s} />)}
                      </div>
                    )}
                  </div>
                ))}

                {/* Add/Edit form */}
                <form onSubmit={handleSaveExp} className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                  <h3 className="font-medium text-gray-900 dark:text-white">
                    {editingExpId ? 'Edit Experience' : 'Add Experience'}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className={labelClass}>Job Title *</label>
                      <input className={inputClass} value={expForm.job_title} onChange={e => setExpForm(p => ({ ...p, job_title: e.target.value }))} required />
                    </div>
                    <div>
                      <label className={labelClass}>Company *</label>
                      <input className={inputClass} value={expForm.company_name} onChange={e => setExpForm(p => ({ ...p, company_name: e.target.value }))} required />
                    </div>
                    <div>
                      <label className={labelClass}>Location</label>
                      <input className={inputClass} value={expForm.location} onChange={e => setExpForm(p => ({ ...p, location: e.target.value }))} />
                    </div>
                    <div className="flex gap-2">
                      <div className="flex-1">
                        <label className={labelClass}>Start Date *</label>
                        <input className={inputClass} value={expForm.start_date} onChange={e => setExpForm(p => ({ ...p, start_date: e.target.value }))} placeholder="YYYY-MM" required />
                      </div>
                      <div className="flex-1">
                        <label className={labelClass}>End Date</label>
                        <input className={inputClass} value={expForm.end_date} onChange={e => setExpForm(p => ({ ...p, end_date: e.target.value }))} placeholder="YYYY-MM" disabled={expForm.is_current} />
                      </div>
                    </div>
                  </div>
                  <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <input type="checkbox" checked={expForm.is_current} onChange={e => setExpForm(p => ({ ...p, is_current: e.target.checked, end_date: '' }))} />
                    Currently working here
                  </label>
                  <div>
                    <label className={labelClass}>Bullet Points</label>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                      Tip: Start with an action verb. Quantify results when possible. Example: "Increased sales pipeline by 35% by implementing automated lead scoring."
                    </p>
                    {expForm.bullet_points.map((b, i) => (
                      <div key={i} className="flex gap-2 mb-2">
                        <input className={inputClass} value={b} onChange={e => updateArrayField(setExpForm, 'bullet_points', i, e.target.value)} placeholder="Describe an accomplishment..." />
                        {expForm.bullet_points.length > 1 && (
                          <button type="button" onClick={() => removeArrayItem(setExpForm, 'bullet_points', i)} className="text-red-500 text-sm">Remove</button>
                        )}
                      </div>
                    ))}
                    <button type="button" onClick={() => addArrayItem(setExpForm, 'bullet_points')} className={btnSecondary}>+ Add Bullet</button>
                  </div>
                  <div>
                    <label className={labelClass}>Skills Used</label>
                    {expForm.skills_used.map((s, i) => (
                      <div key={i} className="flex gap-2 mb-2">
                        <input className={inputClass} value={s} onChange={e => updateArrayField(setExpForm, 'skills_used', i, e.target.value)} placeholder="e.g. Python" />
                        {expForm.skills_used.length > 1 && (
                          <button type="button" onClick={() => removeArrayItem(setExpForm, 'skills_used', i)} className="text-red-500 text-sm">Remove</button>
                        )}
                      </div>
                    ))}
                    <button type="button" onClick={() => addArrayItem(setExpForm, 'skills_used')} className={btnSecondary}>+ Add Skill</button>
                  </div>
                  <div className="flex gap-2">
                    <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : editingExpId ? 'Update' : 'Add Experience'}</button>
                    {editingExpId && <button type="button" onClick={resetExpForm} className={btnSecondary}>Cancel</button>}
                  </div>
                </form>
              </>
            )}
          </div>
        )}

        {/* TAB 2: Education */}
        {activeTab === 2 && userId && (
          <div className="space-y-6">
            {profile?.education?.map(edu => (
              <div key={edu.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg flex justify-between items-start">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">{edu.degree}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{edu.institution} | {edu.graduation_date}</div>
                  {edu.gpa && <div className="text-sm text-gray-500 dark:text-gray-400">GPA: {edu.gpa}</div>}
                  {edu.relevant_coursework?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {edu.relevant_coursework.map((c, i) => <SkillTag key={i} name={c} variant="blue" />)}
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <button onClick={() => editEdu(edu)} className={btnSecondary}>Edit</button>
                  <button onClick={() => handleDeleteEdu(edu.id)} className={btnDanger}>Delete</button>
                </div>
              </div>
            ))}

            <form onSubmit={handleSaveEdu} className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <h3 className="font-medium text-gray-900 dark:text-white">{editingEduId ? 'Edit Education' : 'Add Education'}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className={labelClass}>Degree *</label><input className={inputClass} value={eduForm.degree} onChange={e => setEduForm(p => ({ ...p, degree: e.target.value }))} required placeholder="B.S. Computer Science" /></div>
                <div><label className={labelClass}>Institution *</label><input className={inputClass} value={eduForm.institution} onChange={e => setEduForm(p => ({ ...p, institution: e.target.value }))} required /></div>
                <div><label className={labelClass}>Graduation Date</label><input className={inputClass} value={eduForm.graduation_date} onChange={e => setEduForm(p => ({ ...p, graduation_date: e.target.value }))} placeholder="YYYY-MM" /></div>
                <div><label className={labelClass}>GPA</label><input className={inputClass} value={eduForm.gpa} onChange={e => setEduForm(p => ({ ...p, gpa: e.target.value }))} placeholder="3.8" /></div>
              </div>
              <div>
                <label className={labelClass}>Relevant Coursework</label>
                {eduForm.relevant_coursework.map((c, i) => (
                  <div key={i} className="flex gap-2 mb-2">
                    <input className={inputClass} value={c} onChange={e => updateArrayField(setEduForm, 'relevant_coursework', i, e.target.value)} placeholder="Course name" />
                    {eduForm.relevant_coursework.length > 1 && <button type="button" onClick={() => removeArrayItem(setEduForm, 'relevant_coursework', i)} className="text-red-500 text-sm">Remove</button>}
                  </div>
                ))}
                <button type="button" onClick={() => addArrayItem(setEduForm, 'relevant_coursework')} className={btnSecondary}>+ Add Course</button>
              </div>
              <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : editingEduId ? 'Update' : 'Add Education'}</button>
            </form>
          </div>
        )}

        {/* TAB 3: Skills */}
        {activeTab === 3 && userId && (
          <div className="space-y-6">
            {/* Existing skills grouped by category */}
            {['programming', 'framework', 'tool', 'data', 'soft_skill'].map(cat => {
              const catSkills = profile?.skills?.filter(s => s.category === cat) || [];
              if (catSkills.length === 0) return null;
              return (
                <div key={cat}>
                  <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase mb-2">{cat.replace('_', ' ')}</h3>
                  <div className="flex flex-wrap gap-2">
                    {catSkills.map(s => (
                      <SkillTag key={s.id} name={`${s.skill_name} (${s.proficiency_level})`} onRemove={() => handleDeleteSkill(s.id)} />
                    ))}
                  </div>
                </div>
              );
            })}

            <form onSubmit={handleAddSkill} className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <h3 className="font-medium text-gray-900 dark:text-white">Add Skill</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div><label className={labelClass}>Skill Name *</label><input className={inputClass} value={skillForm.skill_name} onChange={e => setSkillForm(p => ({ ...p, skill_name: e.target.value }))} required placeholder="e.g. Python" /></div>
                <div>
                  <label className={labelClass}>Category</label>
                  <select className={inputClass} value={skillForm.category} onChange={e => setSkillForm(p => ({ ...p, category: e.target.value }))}>
                    <option value="programming">Programming</option>
                    <option value="framework">Framework</option>
                    <option value="tool">Tool</option>
                    <option value="data">Data</option>
                    <option value="soft_skill">Soft Skill</option>
                  </select>
                </div>
                <div>
                  <label className={labelClass}>Proficiency</label>
                  <select className={inputClass} value={skillForm.proficiency_level} onChange={e => setSkillForm(p => ({ ...p, proficiency_level: e.target.value }))}>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
              <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Adding...' : 'Add Skill'}</button>
            </form>
          </div>
        )}

        {/* TAB 4: Projects */}
        {activeTab === 4 && userId && (
          <div className="space-y-6">
            {profile?.projects?.map(proj => (
              <div key={proj.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{proj.project_name}</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">{proj.description}</div>
                    {proj.technologies_used?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {proj.technologies_used.map((t, i) => <SkillTag key={i} name={t} variant="green" />)}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => editProj(proj)} className={btnSecondary}>Edit</button>
                    <button onClick={() => handleDeleteProj(proj.id)} className={btnDanger}>Delete</button>
                  </div>
                </div>
              </div>
            ))}

            <form onSubmit={handleSaveProj} className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <h3 className="font-medium text-gray-900 dark:text-white">{editingProjId ? 'Edit Project' : 'Add Project'}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className={labelClass}>Project Name *</label><input className={inputClass} value={projForm.project_name} onChange={e => setProjForm(p => ({ ...p, project_name: e.target.value }))} required /></div>
                <div><label className={labelClass}>URL</label><input className={inputClass} value={projForm.url} onChange={e => setProjForm(p => ({ ...p, url: e.target.value }))} placeholder="https://github.com/..." /></div>
              </div>
              <div><label className={labelClass}>Description</label><textarea className={inputClass} rows={2} value={projForm.description} onChange={e => setProjForm(p => ({ ...p, description: e.target.value }))} /></div>
              <div>
                <label className={labelClass}>Technologies</label>
                {projForm.technologies_used.map((t, i) => (
                  <div key={i} className="flex gap-2 mb-2">
                    <input className={inputClass} value={t} onChange={e => updateArrayField(setProjForm, 'technologies_used', i, e.target.value)} placeholder="e.g. React" />
                    {projForm.technologies_used.length > 1 && <button type="button" onClick={() => removeArrayItem(setProjForm, 'technologies_used', i)} className="text-red-500 text-sm">Remove</button>}
                  </div>
                ))}
                <button type="button" onClick={() => addArrayItem(setProjForm, 'technologies_used')} className={btnSecondary}>+ Add Tech</button>
              </div>
              <div>
                <label className={labelClass}>Bullet Points</label>
                {projForm.bullet_points.map((b, i) => (
                  <div key={i} className="flex gap-2 mb-2">
                    <input className={inputClass} value={b} onChange={e => updateArrayField(setProjForm, 'bullet_points', i, e.target.value)} />
                    {projForm.bullet_points.length > 1 && <button type="button" onClick={() => removeArrayItem(setProjForm, 'bullet_points', i)} className="text-red-500 text-sm">Remove</button>}
                  </div>
                ))}
                <button type="button" onClick={() => addArrayItem(setProjForm, 'bullet_points')} className={btnSecondary}>+ Add Bullet</button>
              </div>
              <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : editingProjId ? 'Update' : 'Add Project'}</button>
            </form>
          </div>
        )}

        {/* TAB 5: Certifications */}
        {activeTab === 5 && userId && (
          <div className="space-y-6">
            {profile?.certifications?.map(cert => (
              <div key={cert.id} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg flex justify-between items-start">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">{cert.cert_name}</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">{cert.issuing_org} | {cert.date_obtained}</div>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => editCert(cert)} className={btnSecondary}>Edit</button>
                  <button onClick={() => handleDeleteCert(cert.id)} className={btnDanger}>Delete</button>
                </div>
              </div>
            ))}

            <form onSubmit={handleSaveCert} className="space-y-4 pt-4 border-t border-gray-200 dark:border-gray-600">
              <h3 className="font-medium text-gray-900 dark:text-white">{editingCertId ? 'Edit Certification' : 'Add Certification'}</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div><label className={labelClass}>Certification Name *</label><input className={inputClass} value={certForm.cert_name} onChange={e => setCertForm(p => ({ ...p, cert_name: e.target.value }))} required /></div>
                <div><label className={labelClass}>Issuing Organization</label><input className={inputClass} value={certForm.issuing_org} onChange={e => setCertForm(p => ({ ...p, issuing_org: e.target.value }))} /></div>
                <div><label className={labelClass}>Date Obtained</label><input className={inputClass} value={certForm.date_obtained} onChange={e => setCertForm(p => ({ ...p, date_obtained: e.target.value }))} placeholder="YYYY-MM" /></div>
                <div><label className={labelClass}>Expiry Date</label><input className={inputClass} value={certForm.expiry_date} onChange={e => setCertForm(p => ({ ...p, expiry_date: e.target.value }))} placeholder="YYYY-MM" /></div>
                <div className="md:col-span-2"><label className={labelClass}>Credential URL</label><input className={inputClass} value={certForm.credential_url} onChange={e => setCertForm(p => ({ ...p, credential_url: e.target.value }))} /></div>
              </div>
              <button type="submit" className={btnPrimary} disabled={saving}>{saving ? 'Saving...' : editingCertId ? 'Update' : 'Add Certification'}</button>
            </form>
          </div>
        )}

        {/* Not logged in message for sub-tabs */}
        {activeTab > 0 && !userId && (
          <p className="text-gray-500 dark:text-gray-400">Please create your profile in the Personal Info tab first.</p>
        )}
      </div>
    </div>
    <ConfirmDialog
      open={Boolean(pendingDelete)}
      title={`Delete ${pendingDelete?.label || 'item'}?`}
      message="This removes the item from your saved profile and cannot be undone."
      onConfirm={confirmDelete}
      onCancel={() => setPendingDelete(null)}
      confirmLabel={saving ? 'Deleting…' : 'Delete'}
      busy={saving}
    />
    </>
  );
}

export default Profile;
