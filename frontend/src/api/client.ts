import axios from 'axios';
import { toast } from 'sonner';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
      return Promise.reject(error);
    }

    if (!error.response) {
      toast.error('Cannot reach server');
    } else {
      const status = error.response.status;
      const detail = error.response.data?.detail;

      if (typeof detail === 'string') {
        toast.error(detail);
      } else if (status === 404) {
        toast.error('Not found');
      } else if (status === 422) {
        toast.error('Invalid request data');
      } else if (status >= 500) {
        toast.error('Server error. Please try again later.');
      } else {
        toast.error('Something went wrong');
      }
    }

    return Promise.reject(error);
  }
);

export default api;
