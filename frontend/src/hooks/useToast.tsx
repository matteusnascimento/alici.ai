import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

type ToastVariant = 'success' | 'error' | 'warning' | 'info';

interface ToastItem {
  id: number;
  variant: ToastVariant;
  message: string;
}

interface ToastContextValue {
  pushToast: (message: string, variant?: ToastVariant, timeoutMs?: number) => void;
  success: (message: string, timeoutMs?: number) => void;
  error: (message: string, timeoutMs?: number) => void;
  warning: (message: string, timeoutMs?: number) => void;
  info: (message: string, timeoutMs?: number) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const variantStyles: Record<ToastVariant, string> = {
  success: 'border-emerald-300/45 bg-emerald-400/15 text-emerald-100',
  error: 'border-rose-300/45 bg-rose-400/15 text-rose-100',
  warning: 'border-amber-300/45 bg-amber-400/15 text-amber-100',
  info: 'border-cyan-300/45 bg-cyan-400/15 text-cyan-100',
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);

  const pushToast = useCallback((message: string, variant: ToastVariant = 'info', timeoutMs = 2600) => {
    const id = Date.now() + Math.floor(Math.random() * 1000);
    const toast: ToastItem = { id, variant, message };
    setItems((current) => [...current, toast]);
    window.setTimeout(() => {
      setItems((current) => current.filter((item) => item.id !== id));
    }, timeoutMs);
  }, []);

  const success = useCallback((message: string, timeoutMs?: number) => pushToast(message, 'success', timeoutMs), [pushToast]);
  const error = useCallback((message: string, timeoutMs?: number) => pushToast(message, 'error', timeoutMs), [pushToast]);
  const warning = useCallback((message: string, timeoutMs?: number) => pushToast(message, 'warning', timeoutMs), [pushToast]);
  const info = useCallback((message: string, timeoutMs?: number) => pushToast(message, 'info', timeoutMs), [pushToast]);

  const value = useMemo(() => ({ pushToast, success, error, warning, info }), [pushToast, success, error, warning, info]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[120] flex w-[min(92vw,420px)] flex-col gap-2">
        {items.map((item) => (
          <div key={item.id} className={`rounded-xl border px-4 py-3 text-sm shadow-soft backdrop-blur ${variantStyles[item.variant]}`}>
            {item.message}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast precisa ser usado dentro de ToastProvider');
  }
  return context;
}
