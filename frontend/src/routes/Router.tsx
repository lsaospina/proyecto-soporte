import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { AppShell } from '../components/shared/AppShell';
import { DashboardPage } from '../features/dashboard/pages/DashboardPage';
import { ComingSoonPage } from '../pages/ComingSoonPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { CatalogosPage } from '../features/catalogos/pages/CatalogosPage';
import { ActivosDetailPage } from '../features/activos/pages/ActivosDetailPage';
import { ActivosFormPage } from '../features/activos/pages/ActivosFormPage';
import { ActivosListPage } from '../features/activos/pages/ActivosListPage';
import { UsuariosListPage } from '../features/usuarios/pages/UsuariosListPage';
import { UsuarioFormPage } from '../features/usuarios/pages/UsuarioFormPage';
import { MantenimientosPage } from '../features/mantenimientos/pages/MantenimientosPage';

export function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<DashboardPage />} />

            <Route element={<ProtectedRoute roles={['ADMINISTRADOR']} />}>
              <Route path="/catalogos" element={<CatalogosPage />} />
              <Route path="/usuarios" element={<UsuariosListPage />} />
              <Route path="/usuarios/nuevo" element={<UsuarioFormPage />} />
              <Route path="/usuarios/:id/editar" element={<UsuarioFormPage />} />
            </Route>

            <Route element={<ProtectedRoute roles={['ADMINISTRADOR', 'TECNICO']} />}>
              <Route path="/activos" element={<ActivosListPage />} />
              <Route path="/activos/nuevo" element={<ActivosFormPage />} />
              <Route path="/activos/:id" element={<ActivosDetailPage />} />
              <Route path="/activos/:id/editar" element={<ActivosFormPage />} />
              <Route path="/mantenimientos" element={<MantenimientosPage />} />
            </Route>

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
