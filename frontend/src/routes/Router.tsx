import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { AppShell } from '../components/shared/AppShell';
import { DashboardPage } from '../features/dashboard/pages/DashboardPage';
import { ComingSoonPage } from '../pages/ComingSoonPage';
import { NotFoundPage } from '../pages/NotFoundPage';

export function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/activos" element={<ComingSoonPage title="Activos tecnológicos" />} />
            <Route path="/mantenimientos" element={<ComingSoonPage title="Mantenimientos" />} />
            <Route path="/usuarios" element={<ComingSoonPage title="Gestión de usuarios" />} />
            <Route path="/licencias" element={<ComingSoonPage title="Licencias y garantías" />} />
            <Route path="/reportes" element={<ComingSoonPage title="Reportes" />} />
            <Route path="/configuracion" element={<ComingSoonPage title="Configuración" />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
