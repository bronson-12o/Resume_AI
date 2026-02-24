/**
 * API client helper functions for ResumeAI backend.
 */

const API_BASE = '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  // Handle blob responses (file downloads)
  if (response.headers.get('content-type')?.includes('application/vnd')) {
    return response.blob();
  }

  return response.json();
}

// --- Profile ---

export async function createProfile(data) {
  return request('/profile', { method: 'POST', body: JSON.stringify(data) });
}

export async function getProfile(userId) {
  return request(`/profile/${userId}`);
}

export async function listProfiles() {
  return request('/profile');
}

export async function updateProfile(userId, data) {
  return request(`/profile/${userId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteProfile(userId) {
  return request(`/profile/${userId}`, { method: 'DELETE' });
}

// --- Experience ---

export async function addExperience(userId, data) {
  return request(`/profile/${userId}/experience`, { method: 'POST', body: JSON.stringify(data) });
}

export async function updateExperience(userId, expId, data) {
  return request(`/profile/${userId}/experience/${expId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteExperience(userId, expId) {
  return request(`/profile/${userId}/experience/${expId}`, { method: 'DELETE' });
}

// --- Education ---

export async function addEducation(userId, data) {
  return request(`/profile/${userId}/education`, { method: 'POST', body: JSON.stringify(data) });
}

export async function updateEducation(userId, eduId, data) {
  return request(`/profile/${userId}/education/${eduId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteEducation(userId, eduId) {
  return request(`/profile/${userId}/education/${eduId}`, { method: 'DELETE' });
}

// --- Skills ---

export async function addSkill(userId, data) {
  return request(`/profile/${userId}/skills`, { method: 'POST', body: JSON.stringify(data) });
}

export async function updateSkill(userId, skillId, data) {
  return request(`/profile/${userId}/skills/${skillId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteSkill(userId, skillId) {
  return request(`/profile/${userId}/skills/${skillId}`, { method: 'DELETE' });
}

// --- Projects ---

export async function addProject(userId, data) {
  return request(`/profile/${userId}/projects`, { method: 'POST', body: JSON.stringify(data) });
}

export async function updateProject(userId, projId, data) {
  return request(`/profile/${userId}/projects/${projId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteProject(userId, projId) {
  return request(`/profile/${userId}/projects/${projId}`, { method: 'DELETE' });
}

// --- Certifications ---

export async function addCertification(userId, data) {
  return request(`/profile/${userId}/certifications`, { method: 'POST', body: JSON.stringify(data) });
}

export async function updateCertification(userId, certId, data) {
  return request(`/profile/${userId}/certifications/${certId}`, { method: 'PUT', body: JSON.stringify(data) });
}

export async function deleteCertification(userId, certId) {
  return request(`/profile/${userId}/certifications/${certId}`, { method: 'DELETE' });
}

// --- Jobs ---

export async function parseJobDescription(jobDescription) {
  return request('/jobs/parse', { method: 'POST', body: JSON.stringify({ job_description: jobDescription }) });
}

// --- Scoring ---

export async function getMatchScore(userId, parsedJob) {
  return request('/scoring/match', { method: 'POST', body: JSON.stringify({ user_id: userId, parsed_job: parsedJob }) });
}

// --- Resume ---

export async function generateResume(userId, jobDescription, parsedJob = null) {
  return request('/resume/generate', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, job_description: jobDescription, parsed_job: parsedJob }),
  });
}

export async function getResume(resumeId) {
  return request(`/resume/${resumeId}`);
}

export async function getResumeHistory(userId) {
  return request(`/resume/history/${userId}`);
}

export async function downloadResume(resumeId) {
  const blob = await request(`/resume/${resumeId}/download`);
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `resume_${resumeId}.docx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// --- Recommendations ---

export async function getSkillRecommendations(userId, matchResult) {
  return request('/recommendations/skills', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId, match_result: matchResult }),
  });
}

export async function getSectorSuggestions(userId) {
  return request('/recommendations/sectors', { method: 'POST', body: JSON.stringify({ user_id: userId }) });
}
