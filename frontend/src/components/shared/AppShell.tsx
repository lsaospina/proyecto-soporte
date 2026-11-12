import { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/hooks/useAuth';
import {
  LayoutDashboard,
  Monitor,
  Wrench,
  Users,
  FileKey,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  ChevronLeft,
} from 'lucide-react';

import type { UserRole } from '../../features/auth/types';

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  roles: UserRole[];
}

const navItems: NavItem[] = [
  { label: 'Dashboard', to: '/dashboard', icon: <LayoutDashboard size={20} />, roles: ['ADMINISTRADOR'] },
  { label: 'Activos', to: '/activos', icon: <Monitor size={20} />, roles: ['ADMINISTRADOR', 'TECNICO', 'USUARIO_RESPONSABLE'] },
  { label: 'Mantenimientos', to: '/mantenimientos', icon: <Wrench size={20} />, roles: ['ADMINISTRADOR', 'TECNICO'] },
  { label: 'Usuarios', to: '/usuarios', icon: <Users size={20} />, roles: ['ADMINISTRADOR'] },
  { label: 'Licencias y garantías', to: '/licencias', icon: <FileKey size={20} />, roles: ['ADMINISTRADOR'] },
  { label: 'Reportes', to: '/reportes', icon: <BarChart3 size={20} />, roles: ['ADMINISTRADOR'] },
  { label: 'Configuración', to: '/configuracion', icon: <Settings size={20} />, roles: ['ADMINISTRADOR'] },
];

const roleLabels: Record<UserRole, string> = {
  ADMINISTRADOR: 'Administrador',
  TECNICO: 'Técnico',
  USUARIO_RESPONSABLE: 'Usuario Responsable',
};

export function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const userRole = user?.rol ?? 'USUARIO_RESPONSABLE';
  const filteredNav = navItems.filter((item) => item.roles.includes(userRole));

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside
        style={{
          width: sidebarCollapsed ? '64px' : '256px',
          backgroundColor: 'var(--surface-lowest)',
          color: 'var(--text)',
          borderRight: '1px solid var(--border)',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width var(--transition-fast)',
          position: 'fixed',
          top: 0,
          left: 0,
          bottom: 0,
          zIndex: 50,
          overflow: 'hidden',
        }}
        className="sidebar-desktop"
      >
        {/* Logo area */}
        <div
          style={{
            padding: sidebarCollapsed ? '16px 12px' : '16px 20px',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: sidebarCollapsed ? 'center' : 'space-between',
            minHeight: '64px',
          }}
        >
          {!sidebarCollapsed && (
            <div>
              <div style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text)', letterSpacing: '-0.02em' }}>
                ITAM
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Gestión de activos
              </div>
            </div>
          )}
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            aria-label={sidebarCollapsed ? 'Expandir menú' : 'Colapsar menú'}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <ChevronLeft
              size={18}
              style={{
                transform: sidebarCollapsed ? 'rotate(180deg)' : 'none',
                transition: 'transform var(--transition-fast)',
              }}
            />
          </button>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '8px', overflow: 'auto' }}>
          {filteredNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: sidebarCollapsed ? '10px 12px' : '10px 12px',
                borderRadius: 'var(--radius-control)',
                color: isActive ? 'var(--primary)' : 'var(--text-muted)',
                backgroundColor: isActive ? 'var(--primary-light)' : 'transparent',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 400,
                marginBottom: '2px',
                transition: 'all var(--transition-fast)',
                justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
                whiteSpace: 'nowrap',
              })}
              title={sidebarCollapsed ? item.label : undefined}
            >
              <span style={{ flexShrink: 0 }}>{item.icon}</span>
              {!sidebarCollapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User info + logout */}
        <div
          style={{
            padding: sidebarCollapsed ? '12px' : '12px 16px',
            borderTop: '1px solid var(--border)',
          }}
        >
          {!sidebarCollapsed && user && (
            <div style={{ marginBottom: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {user.nombre_completo}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                {roleLabels[user.rol]}
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              width: '100%',
              padding: '8px 12px',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              borderRadius: 'var(--radius-control)',
              fontSize: '13px',
              justifyContent: sidebarCollapsed ? 'center' : 'flex-start',
            }}
            title="Cerrar sesión"
          >
            <LogOut size={18} />
            {!sidebarCollapsed && <span>Cerrar sesión</span>}
          </button>
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileMenuOpen && (
        <div
          onClick={() => setMobileMenuOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 40,
          }}
        />
      )}

      {/* Main content */}
      <div
        style={{
          flex: 1,
          marginLeft: sidebarCollapsed ? '64px' : '256px',
          transition: 'margin-left var(--transition-fast)',
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}
      >
        {/* Topbar */}
        <header
          style={{
            height: '64px',
            backgroundColor: 'var(--surface)',
            borderBottom: '1px solid var(--border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0 24px',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          <button
            onClick={() => setMobileMenuOpen(true)}
            aria-label="Abrir menú"
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--text)',
              padding: '4px',
              display: 'none', // Show only on mobile via media query
            }}
            className="mobile-menu-btn"
          >
            <Menu size={24} />
          </button>
          <div />
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {user && (
              <>
                <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  {user.nombre_completo}
                </span>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    padding: '2px 10px',
                    fontSize: '11px',
                    fontWeight: 500,
                    borderRadius: '9999px',
                    color: 'var(--info-fg)',
                    backgroundColor: 'var(--info-bg)',
                  }}
                >
                  {roleLabels[user.rol]}
                </span>
              </>
            )}
          </div>
        </header>

        {/* Page content */}
        <main style={{ flex: 1, padding: '24px', maxWidth: '1280px', width: '100%' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
