import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import RouteErrorBoundary from '../RouteErrorBoundary';

export default function AppLayout() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <Navbar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        <RouteErrorBoundary key={location.pathname}>
          <Outlet />
        </RouteErrorBoundary>
      </main>
    </div>
  );
}
