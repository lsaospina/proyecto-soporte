import { AlertCircle } from 'lucide-react';

interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message = 'Ocurrió un error inesperado.', onRetry }: ErrorStateProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      backgroundColor: '#FEE2E2',
      border: '1px solid #FECACA',
      borderRadius: '8px',
      textAlign: 'center',
    }}>
      <AlertCircle size={48} style={{ color: '#B91C1C', marginBottom: '16px' }} />
      <p style={{ fontSize: '14px', color: '#B91C1C', margin: '0 0 16px' }}>{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            padding: '8px 20px',
            backgroundColor: '#B91C1C',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 500,
          }}
        >
          Reintentar
        </button>
      )}
    </div>
  );
}
