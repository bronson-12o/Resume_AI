import { fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it } from 'vitest';
import { Link, matchPath, RouterProvider, useRouter } from './router';

function RouteProbe() {
  const { pathname } = useRouter();
  return (
    <div>
      <span data-testid="path">{pathname}</span>
      <Link to="/profile">Open profile</Link>
    </div>
  );
}

describe('client router', () => {
  beforeEach(() => window.history.replaceState({}, '', '/'));

  it('matches dynamic result routes without accepting extra segments', () => {
    expect(matchPath('/results/:resumeId', '/results/42')).toEqual({ params: { resumeId: '42' } });
    expect(matchPath('/results/:resumeId', '/results/42/edit')).toBeNull();
    expect(matchPath('/results/:resumeId', '/results/%E0%A4%A')).toBeNull();
  });

  it('updates the rendered route through an accessible link', () => {
    render(<RouterProvider><RouteProbe /></RouterProvider>);
    fireEvent.click(screen.getByRole('link', { name: 'Open profile' }));
    expect(screen.getByTestId('path')).toHaveTextContent('/profile');
    expect(window.location.pathname).toBe('/profile');
  });
});
