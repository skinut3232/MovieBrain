import { Link, useNavigate } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';

export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-amber-400 text-center mb-8">
          MovieBrain
        </h1>
        <div className="bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Login</h2>
          <LoginForm onSuccess={() => navigate('/')} />
          <p className="mt-4 text-sm text-gray-400 text-center">
            Don't have an account?{' '}
            <Link to="/register" className="text-amber-400 hover:underline">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
