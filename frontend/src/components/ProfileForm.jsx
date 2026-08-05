/**
 * Reusable form field component for profile editing.
 */
import { useId } from 'react';

function ProfileForm({ label, value, onChange, type = 'text', required = false, placeholder = '' }) {
  const inputId = useId();

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
      </label>
      <input
        id={inputId}
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
      />
    </div>
  );
}

export default ProfileForm;
