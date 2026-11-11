import { useNavigate } from 'react-router-dom';
import { FileQuestion } from 'lucide-react';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      backgroundColor: 'var(--background)',
      color: 'var(--text)',
      gap: '16px',
      padding: '24px',
    }}>
      <FileQuestion size={64} style={{ color: 'var(--text-muted)' }} />
      <h1 style={{ fontSize: '24px', fontWeight: 600, margin: 0 }}>Página no encontrada</h1>
      <p style={{ color: 'var(--text-muted)', margin: 0 }}>La página que buscas no existe o fue movida.</p>
      <button
        onClick={() => navigate('/dashboard')}
        style={{
          marginTop: '8px',
          padding: '10px 24px',
          backgroundColor: 'var(--primary)',
          color: '#FFFFFF',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer',
          fontSize: '14px',
          fontWeight: 500,
        }}
      >
        Ir al inicio
      </button>
    </div>
  );
}
