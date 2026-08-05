import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

const RouterContext = createContext(null);

function currentPath() {
  return `${window.location.pathname}${window.location.search}${window.location.hash}`;
}

export function matchPath(pattern, pathname) {
  const patternParts = pattern.split('/').filter(Boolean);
  const pathParts = pathname.split('?')[0].split('#')[0].split('/').filter(Boolean);
  if (patternParts.length !== pathParts.length) return null;

  const params = {};
  for (let index = 0; index < patternParts.length; index += 1) {
    const patternPart = patternParts[index];
    const pathPart = pathParts[index];
    if (patternPart.startsWith(':')) {
      try {
        params[patternPart.slice(1)] = decodeURIComponent(pathPart);
      } catch {
        return null;
      }
    } else if (patternPart !== pathPart) {
      return null;
    }
  }
  return { params };
}

export function RouterProvider({ children }) {
  const [path, setPath] = useState(currentPath);

  useEffect(() => {
    const handlePopState = () => setPath(currentPath());
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = useCallback((to, { replace = false } = {}) => {
    const target = new URL(to, window.location.origin);
    if (target.origin !== window.location.origin) {
      window.location.assign(target.href);
      return;
    }
    const nextPath = `${target.pathname}${target.search}${target.hash}`;
    window.history[replace ? 'replaceState' : 'pushState']({}, '', nextPath);
    setPath(nextPath);
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, []);

  const value = useMemo(
    () => ({ pathname: path.split('?')[0].split('#')[0], path, navigate }),
    [navigate, path],
  );

  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}

export function useRouter() {
  const context = useContext(RouterContext);
  if (!context) throw new Error('Router hooks must be used inside RouterProvider');
  return context;
}

export function useNavigate() {
  return useRouter().navigate;
}

export function useParams() {
  const { pathname } = useRouter();
  return matchPath('/results/:resumeId', pathname)?.params || {};
}

export function Link({ to, onClick, children, ...props }) {
  const navigate = useNavigate();

  function handleClick(event) {
    onClick?.(event);
    if (
      event.defaultPrevented ||
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    ) return;

    event.preventDefault();
    navigate(to);
  }

  return <a href={to} onClick={handleClick} {...props}>{children}</a>;
}

export function NavLink({ to, end = false, className, children, ...props }) {
  const { pathname } = useRouter();
  const isActive = end ? pathname === to : pathname === to || pathname.startsWith(`${to}/`);
  const resolvedClassName = typeof className === 'function' ? className({ isActive }) : className;

  return (
    <Link
      to={to}
      className={resolvedClassName}
      aria-current={isActive ? 'page' : undefined}
      {...props}
    >
      {children}
    </Link>
  );
}
