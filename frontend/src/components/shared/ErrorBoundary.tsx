import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error) {
    console.error('ErrorBoundary:', error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 24, textAlign: 'center' }}>
          <h2>Ha ocurrido un error inesperado.</h2>
          {import.meta.env.DEV && this.state.error && (
            <pre style={{ marginTop: 12, textAlign: 'left', color: 'var(--danger-fg)', whiteSpace: 'pre-wrap' }}>
              {this.state.error.message}
              {'\n'}
              {this.state.error.stack}
            </pre>
          )}
          <button onClick={() => window.location.reload()} style={{ marginTop: 12, padding: '8px 16px' }}>
            Recargar
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

