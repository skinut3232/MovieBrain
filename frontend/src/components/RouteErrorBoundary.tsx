import { Link } from 'react-router-dom';
import ErrorBoundary from './ErrorBoundary';
import type { ReactNode } from 'react';

export default function RouteErrorBoundary({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="flex items-center justify-center min-h-[400px] p-4">
          <div className="bg-gray-800 rounded-xl p-8 max-w-md w-full text-center space-y-4">
            <h2 className="text-xl font-bold text-gray-100">Something went wrong</h2>
            <p className="text-gray-400 text-sm">This page encountered an error.</p>
            <div className="flex gap-3 justify-center">
              <button
                onClick={() => window.location.reload()}
                className="bg-amber-500 text-black font-semibold px-6 py-2 rounded-lg hover:bg-amber-400 transition-colors"
              >
                Try Again
              </button>
              <Link
                to="/explore"
                className="bg-gray-700 text-gray-200 font-semibold px-6 py-2 rounded-lg hover:bg-gray-600 transition-colors"
              >
                Go to Explore
              </Link>
            </div>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}
