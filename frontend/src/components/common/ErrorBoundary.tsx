import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, message: '' };
  }

  static getDerivedStateFromError(error: unknown): State {
    const message =
      error instanceof Error ? error.message : 'Erro desconhecido';
    return { hasError: true, message };
  }

  override componentDidCatch(error: unknown, info: ErrorInfo) {
    if (import.meta.env.DEV) {
      console.error('[ErrorBoundary] Componente quebrou:', error, info.componentStack);
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, message: '' });
  };

  override render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8 text-center">
          <div className="rounded-3xl border border-rose-400/30 bg-rose-500/10 px-8 py-6 max-w-md w-full">
            <p className="text-sm uppercase tracking-[0.2em] text-rose-300">Erro ao renderizar</p>
            <p className="mt-2 text-sm text-slate-300">{this.state.message}</p>
            <button
              type="button"
              onClick={this.handleReset}
              className="mt-4 rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
            >
              Tentar novamente
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
