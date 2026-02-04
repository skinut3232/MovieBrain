import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useProfile } from '../../context/ProfileContext';

export default function Navbar() {
  const { logout } = useAuth();
  const { profiles, activeProfile, setActiveProfile } = useProfile();
  const navigate = useNavigate();

  return (
    <nav className="bg-gray-900 text-white px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <Link to="/" className="text-xl font-bold text-amber-400">
          MovieBrain
        </Link>
        <Link to="/search" className="hover:text-amber-300">
          Search
        </Link>
        <Link to="/history" className="hover:text-amber-300">
          History
        </Link>
        <Link to="/recommend" className="hover:text-amber-300">
          Recommend
        </Link>
        <Link to="/lists" className="hover:text-amber-300">
          Lists
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {profiles.length > 0 && (
          <select
            value={activeProfile?.id ?? ''}
            onChange={(e) => {
              const p = profiles.find(
                (p) => p.id === Number(e.target.value)
              );
              if (p) setActiveProfile(p);
            }}
            className="bg-gray-800 text-white border border-gray-600 rounded px-2 py-1 text-sm"
          >
            {profiles.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        )}
        <button
          onClick={() => {
            logout();
            navigate('/login');
          }}
          className="text-sm text-gray-400 hover:text-white"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}
