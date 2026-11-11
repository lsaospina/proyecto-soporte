import { ChevronRight } from 'lucide-react';

interface Breadcrumb {
  label: string;
  href?: string;
}

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumbs?: Breadcrumb[];
  actions?: React.ReactNode;
}

export function PageHeader({ title, subtitle, breadcrumbs, actions }: PageHeaderProps) {
  return (
    <div style={{ marginBottom: '24px' }}>
      {breadcrumbs && breadcrumbs.length > 0 && (
        <nav style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
          {breadcrumbs.map((crumb, index) => (
            <span key={index} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              {index > 0 && <ChevronRight size={14} />}
              {crumb.href ? (
                <a href={crumb.href} style={{ color: 'var(--primary)', textDecoration: 'none' }}>{crumb.label}</a>
              ) : (
                <span>{crumb.label}</span>
              )}
            </span>
          ))}
        </nav>
      )}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '24px', fontWeight: 600, color: 'var(--text)', margin: 0 }}>{title}</h1>
          {subtitle && <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: '4px 0 0' }}>{subtitle}</p>}
        </div>
        {actions && <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>{actions}</div>}
      </div>
    </div>
  );
}
