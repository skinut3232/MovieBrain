import { Link, useNavigate } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';

export default function RegisterPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-3xl font-bold text-amber-400 text-center mb-8">
          MovieBrain
        </h1>
        <div className="bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            Create Account
          </h2>
          <RegisterForm onSuccess={() => navigate('/')} />
          <p className="mt-4 text-sm text-gray-400 text-center">
            Already have an account?{' '}
            <Link to="/login" className="text-amber-400 hover:underline">
              Login
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
