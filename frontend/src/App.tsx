import { Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import { useAuth } from './context/AuthContext';
import HomePage from './pages/HomePage';
import ListDetailPage from './pages/ListDetailPage';
import ListsPageWrapper from './pages/ListsPageWrapper';
import LoginPage from './pages/LoginPage';
import MovieDetailPage from './pages/MovieDetailPage';
import RegisterPage from './pages/RegisterPage';
import SearchPage from './pages/SearchPage';
import RecommendPage from './pages/RecommendPage';
import WatchHistoryPage from './pages/WatchHistoryPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/movie/:titleId" element={<MovieDetailPage />} />
        <Route path="/history" element={<WatchHistoryPage />} />
        <Route path="/recommend" element={<RecommendPage />} />
        <Route path="/lists" element={<ListsPageWrapper />} />
        <Route path="/lists/:listId" element={<ListDetailPage />} />
      </Route>
    </Routes>
  );
}
