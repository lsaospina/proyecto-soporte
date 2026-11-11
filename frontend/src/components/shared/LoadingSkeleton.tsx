interface LoadingSkeletonProps {
  lines?: number;
  width?: string;
}

export function LoadingSkeleton({ lines = 3, width = '100%' }: LoadingSkeletonProps) {
  return (
    <div style={{ width, display: 'flex', flexDirection: 'column', gap: '12px' }} role="status" aria-label="Cargando...">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton-pulse"
          style={{
            height: '16px',
            borderRadius: '4px',
            backgroundColor: 'var(--border)',
            width: i === lines - 1 ? '60%' : '100%',
          }}
        />
      ))}
    </div>
  );
}
