import { AuthProvider } from './features/auth/hooks/useAuth';
import { Router } from './routes/Router';

export default function App() {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
}
