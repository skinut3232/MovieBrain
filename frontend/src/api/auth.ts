import type { TokenResponse } from '../types';
import api from './client';

export async function register(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/register', { email, password });
  return data;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);
  const { data } = await api.post<TokenResponse>('/auth/login', params, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  return data;
}
