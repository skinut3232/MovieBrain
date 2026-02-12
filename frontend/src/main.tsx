import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'sonner'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './context/AuthContext.tsx'
import { ProfileProvider } from './context/ProfileContext.tsx'
import ErrorBoundary from './components/ErrorBoundary.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ProfileProvider>
          <ErrorBoundary>
            <App />
          </ErrorBoundary>
        </ProfileProvider>
      </AuthProvider>
    </BrowserRouter>
    <Toaster
      position="bottom-right"
      theme="dark"
      toastOptions={{
        style: { background: '#1f2937', border: '1px solid #374151' },
      }}
    />
  </StrictMode>,
)
