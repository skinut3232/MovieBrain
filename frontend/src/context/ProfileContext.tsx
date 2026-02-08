import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import * as profilesApi from '../api/profiles';
import type { Profile } from '../types';
import { useAuth } from './AuthContext';

interface ProfileContextValue {
  profiles: Profile[];
  activeProfile: Profile | null;
  setActiveProfile: (p: Profile) => void;
  refreshProfiles: () => Promise<void>;
  createProfile: (name: string) => Promise<Profile>;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function ProfileProvider({ children }: { children: ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [activeProfile, setActiveProfile] = useState<Profile | null>(null);

  const refreshProfiles = useCallback(async () => {
    if (!isAuthenticated) return;
    try {
      const list = await profilesApi.getProfiles();
      setProfiles(list);
      if (list.length > 0 && !activeProfile) {
        setActiveProfile(list[0]);
      }
    } catch {
      // Profile fetch failed — keep existing state
    }
  }, [isAuthenticated, activeProfile]);

  const createProfile = useCallback(
    async (name: string) => {
      const profile = await profilesApi.createProfile(name);
      setProfiles((prev) => [...prev, profile]);
      if (!activeProfile) {
        setActiveProfile(profile);
      }
      return profile;
    },
    [activeProfile]
  );

  // Note: createProfile intentionally does NOT catch — callers handle the error

  useEffect(() => {
    if (isAuthenticated) {
      refreshProfiles();
    } else {
      setProfiles([]);
      setActiveProfile(null);
    }
  }, [isAuthenticated]);

  return (
    <ProfileContext.Provider
      value={{
        profiles,
        activeProfile,
        setActiveProfile,
        refreshProfiles,
        createProfile,
      }}
    >
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  const ctx = useContext(ProfileContext);
  if (!ctx) throw new Error('useProfile must be used within ProfileProvider');
  return ctx;
}
