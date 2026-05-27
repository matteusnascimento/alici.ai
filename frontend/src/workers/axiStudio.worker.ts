type WorkerRequest =
  | { type: 'autosave'; key: string; payload: unknown }
  | { type: 'estimate-video'; clips: Array<{ duration: number }> }
  | { type: 'render-plan'; payload: unknown };

type WorkerResponse =
  | { type: 'autosave:done'; key: string; savedAt: string }
  | { type: 'estimate-video:done'; duration: number; sizeHintMb: number }
  | { type: 'render-plan:done'; commands: string[] };

function post(message: WorkerResponse) {
  self.postMessage(message);
}

self.onmessage = (event: MessageEvent<WorkerRequest>) => {
  const message = event.data;

  if (message.type === 'autosave') {
    localStorage.setItem(message.key, JSON.stringify({ payload: message.payload, savedAt: new Date().toISOString() }));
    post({ type: 'autosave:done', key: message.key, savedAt: new Date().toISOString() });
    return;
  }

  if (message.type === 'estimate-video') {
    const duration = message.clips.reduce((total, clip) => total + Math.max(0, Number(clip.duration) || 0), 0);
    post({ type: 'estimate-video:done', duration, sizeHintMb: Math.max(1, Math.round(duration * 2.4)) });
    return;
  }

  if (message.type === 'render-plan') {
    post({
      type: 'render-plan:done',
      commands: [
        'normalize-media',
        'compose-layers',
        'mix-audio',
        'encode-h264',
      ],
    });
  }
};

export {};
