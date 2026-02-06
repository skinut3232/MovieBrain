import type { OnboardingMoviesResponse } from '../types';
import api from './client';

export async function getOnboardingMovies(
  profileId: number,
  limit: number = 10
): Promise<OnboardingMoviesResponse> {
  const { data } = await api.get<OnboardingMoviesResponse>(
    `/profiles/${profileId}/onboarding-movies`,
    { params: { limit } }
  );
  return data;
}

export async function skipOnboardingMovie(
  profileId: number,
  titleId: number
): Promise<void> {
  await api.post(`/profiles/${profileId}/onboarding-skip`, { title_id: titleId });
}

export async function completeOnboarding(
  profileId: number
): Promise<void> {
  await api.post(`/profiles/${profileId}/onboarding-complete`);
}
