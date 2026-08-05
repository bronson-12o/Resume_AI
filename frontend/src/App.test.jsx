import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import App from './App';

beforeEach(() => {
  window.history.replaceState({}, '', '/');
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    headers: new Headers({ 'content-type': 'application/json' }),
    json: async () => ({ items: [], total: 0, skip: 0, limit: 50 }),
  }));
});

afterEach(() => vi.unstubAllGlobals());

it('renders honest onboarding and exposes all primary destinations', async () => {
  render(<App />);

  expect(await screen.findByRole('heading', {
    name: 'Build a stronger application from the experience you already have.',
  })).toBeInTheDocument();
  expect(screen.getByText('Your data stays in this installation.', { exact: false })).toBeInTheDocument();
  expect(screen.getAllByRole('link', { name: 'Tracker' })).toHaveLength(2);
  expect(screen.getByRole('link', { name: 'Get Started — Create Profile' })).toHaveAttribute('href', '/profile');
});
