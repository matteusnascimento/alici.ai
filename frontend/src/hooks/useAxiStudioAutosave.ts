import { useEffect, useMemo, useRef, useState } from 'react';

import { getAxiStudioSnapshot, useAxiStudioStore } from '../store/axiStudioStore';

interface AutosaveStatus {
  status: 'idle' | 'saving' | 'saved' | 'error';
  savedAt: string | null;
}

export function useAxiStudioAutosave(storageKey = 'axi_studio_autosave') {
  const dirty = useAxiStudioStore((state) => state.dirty);
  const markSaved = useAxiStudioStore((state) => state.markSaved);
  const [state, setState] = useState<AutosaveStatus>({ status: 'idle', savedAt: null });
  const workerRef = useRef<Worker | null>(null);

  const worker = useMemo(() => {
    if (typeof Worker === 'undefined') return null;
    return new Worker(new URL('../workers/axiStudio.worker.ts', import.meta.url), { type: 'module' });
  }, []);

  useEffect(() => {
    workerRef.current = worker;
    if (!worker) return undefined;

    worker.onmessage = (event: MessageEvent<{ type: string; savedAt?: string }>) => {
      if (event.data.type === 'autosave:done') {
        markSaved();
        setState({ status: 'saved', savedAt: event.data.savedAt ?? new Date().toISOString() });
      }
    };

    worker.onerror = () => setState((current) => ({ ...current, status: 'error' }));

    return () => {
      worker.terminate();
      workerRef.current = null;
    };
  }, [markSaved, worker]);

  useEffect(() => {
    if (!dirty) return undefined;

    const timer = window.setTimeout(() => {
      const payload = getAxiStudioSnapshot();
      setState((current) => ({ ...current, status: 'saving' }));

      try {
        if (workerRef.current) {
          workerRef.current.postMessage({ type: 'autosave', key: storageKey, payload });
        } else {
          localStorage.setItem(storageKey, JSON.stringify({ payload, savedAt: new Date().toISOString() }));
          markSaved();
          setState({ status: 'saved', savedAt: new Date().toISOString() });
        }
      } catch {
        setState((current) => ({ ...current, status: 'error' }));
      }
    }, 900);

    return () => window.clearTimeout(timer);
  }, [dirty, markSaved, storageKey]);

  return state;
}
