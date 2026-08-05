import { Toaster } from 'react-hot-toast';
import { useState, useEffect } from 'react';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Tailor from './pages/Tailor';
import Results from './pages/Results';
import Tracker from './pages/Tracker';
import ErrorBoundary from './components/ErrorBoundary';
import { Link, matchPath, NavLink, RouterProvider, useRouter } from './router';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/profile', label: 'Profile' },
  { to: '/tailor', label: 'Tailor' },
  { to: '/tracker', label: 'Tracker' },
];

function NotFound() {
  return (
    <section className="surface-card p-8 text-center">
      <p className="eyebrow">404</p>
      <h1 className="mt-2 text-2xl font-bold text-slate-950 dark:text-white">Page not found</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-300">The page may have moved or the address is incomplete.</p>
      <Link to="/" className="button-primary mt-6">Return to dashboard</Link>
    </section>
  );
}

function AppShell() {
  const { pathname } = useRouter();
  const [darkMode, setDarkMode] = useState(() => {
    let saved = null;
    try {
      saved = window.localStorage?.getItem('darkMode') ?? null;
    } catch {
      // Storage can be unavailable in privacy-restricted browser contexts.
    }
    return saved === null ? window.matchMedia('(prefers-color-scheme: dark)').matches : saved === 'true';
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    try {
      window.localStorage?.setItem('darkMode', String(darkMode));
    } catch {
      // The theme still applies for this session when storage is unavailable.
    }
  }, [darkMode]);

  const desktopNavLinkClass = ({ isActive }) =>
    `rounded-lg px-3 py-2 text-sm font-semibold transition-colors ${
      isActive
        ? 'bg-primary-600 text-white shadow-sm'
        : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-white'
    }`;

  const mobileNavLinkClass = ({ isActive }) =>
    `flex min-w-0 flex-col items-center justify-center gap-1 rounded-xl px-2 py-2 text-xs font-semibold transition-colors ${
      isActive
        ? 'bg-primary-50 text-primary-700 dark:bg-primary-950/60 dark:text-primary-300'
        : 'text-slate-500 dark:text-slate-400'
    }`;

  let page = <NotFound />;
  if (pathname === '/') page = <Dashboard />;
  else if (pathname === '/profile') page = <Profile />;
  else if (pathname === '/tailor') page = <Tailor />;
  else if (pathname === '/tracker') page = <Tracker />;
  else if (matchPath('/results/:resumeId', pathname)) page = <Results />;

  return (
      <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-slate-950 dark:text-slate-50">
        <Toaster position="top-right" toastOptions={{ duration: 4500 }} />
        <a href="#main-content" className="skip-link">Skip to content</a>

        <header className="sticky top-0 z-40 border-b border-slate-200/90 bg-white/95 backdrop-blur dark:border-slate-800 dark:bg-slate-950/95">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link to="/" className="flex items-center gap-2 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500">
                <span aria-hidden="true" className="grid h-9 w-9 place-items-center rounded-xl bg-primary-600 text-sm font-black text-white shadow-sm">R</span>
                <span className="text-lg font-bold tracking-tight text-slate-950 dark:text-white">ResumeAI</span>
              </Link>

              <div className="flex items-center gap-2">
                <nav aria-label="Primary" className="hidden items-center gap-1 md:flex">
                  {NAV_ITEMS.map((item) => (
                    <NavLink key={item.to} to={item.to} end={item.end} className={desktopNavLinkClass}>
                      {item.label}
                    </NavLink>
                  ))}
                </nav>

                <button
                  onClick={() => setDarkMode(!darkMode)}
                  className="ml-1 rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-950 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
                  aria-label={darkMode ? 'Use light theme' : 'Use dark theme'}
                  title={darkMode ? 'Use light theme' : 'Use dark theme'}
                >
                  {darkMode ? (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                    </svg>
                  ) : (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>
          </div>
        </header>

        <main id="main-content" className="mx-auto max-w-7xl px-4 py-6 pb-28 sm:px-6 md:py-10 md:pb-12 lg:px-8">
          <ErrorBoundary>
            {page}
          </ErrorBoundary>
        </main>

        <nav aria-label="Mobile primary" className="fixed inset-x-0 bottom-0 z-40 border-t border-slate-200 bg-white/95 px-3 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 backdrop-blur md:hidden dark:border-slate-800 dark:bg-slate-950/95">
          <div className="mx-auto grid max-w-md grid-cols-4 gap-1">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end} className={mobileNavLinkClass}>
                <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-current" />
                {item.label}
              </NavLink>
            ))}
          </div>
        </nav>
      </div>
  );
}

function App() {
  return <RouterProvider><AppShell /></RouterProvider>;
}

export default App;
