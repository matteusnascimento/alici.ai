import type { AccountPreferences } from '../../types/account';

interface PreferencesFormProps {
  value: AccountPreferences;
  onChange: (next: AccountPreferences) => void;
  onSave: () => Promise<void>;
  saving: boolean;
  saveStatus?: 'idle' | 'success' | 'error';
  saveMessage?: string;
}

interface CardProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}

interface SelectProps {
  label: string;
  description: string;
  options: string[];
  value: string;
  onChange: (next: string) => void;
}

interface ToggleProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}

const Card = ({ title, subtitle, children }: CardProps) => (
  <div className="bg-[#0F172A] p-6 rounded-2xl border border-white/5 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)]">
    <h3 className="text-white text-lg font-semibold">{title}</h3>
    <p className="mt-1 text-sm text-slate-300">{subtitle}</p>
    <div className="mt-5 space-y-4">{children}</div>
  </div>
);

const Select = ({ label, description, options, value, onChange }: SelectProps) => (
  <div className="rounded-xl border border-white/10 bg-black/20 p-4">
    <div className="flex flex-wrap items-start justify-between gap-4">
      <div className="max-w-[70%]">
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="mt-1 text-xs text-slate-300">{description}</p>
      </div>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-w-[210px] rounded-lg border border-white/10 bg-black/40 px-3 py-2.5 text-sm text-white outline-none transition hover:border-white/20 focus:border-cyan/60"
      >
        {options.map((opt) => (
          <option key={opt}>{opt}</option>
        ))}
      </select>
    </div>
  </div>
);

const Toggle = ({ label, description, checked, onChange }: ToggleProps) => (
  <div className="rounded-xl border border-white/10 bg-black/20 p-4">
    <label className="flex cursor-pointer items-start justify-between gap-4">
      <div className="max-w-[75%]">
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="mt-1 text-xs text-slate-300">{description}</p>
      </div>
      <span className="relative inline-flex h-6 w-11 shrink-0">
        <input
          type="checkbox"
          checked={checked}
          onChange={(event) => onChange(event.target.checked)}
          className="peer sr-only"
        />
        <span className="absolute inset-0 rounded-full bg-white/20 transition peer-checked:bg-cyan/80 peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-cyan/70" />
        <span className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition peer-checked:translate-x-5" />
      </span>
    </label>
  </div>
);

export function PreferencesForm({ value, onChange, onSave, saving, saveStatus = 'idle', saveMessage }: PreferencesFormProps) {
  const selectOptions = {
    theme_mode: ['system', 'light', 'dark'],
    accent_color: ['cyan', 'blue', 'green', 'orange', 'amber'],
    language: ['pt-BR', 'en-US', 'es-ES'],
    voice: ['alloy', 'nova', 'echo', 'fable', 'shimmer'],
  } as const;

  const withCurrentValue = (options: string[], current: string) => (options.includes(current) ? options : [current, ...options]);

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6 md:p-7">
      <h2 className="font-display text-2xl text-white">Personalização</h2>
      <p className="mt-2 text-sm text-slate-300">Ajuste aparência, idioma e comportamento da AXI para uma experiência mais fluida no dia a dia.</p>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card title="Aparência" subtitle="Defina como a AXI será exibida visualmente para você.">
          <Select
            label="Tema"
            description="Escolha como a interface da AXI será exibida para você."
            value={value.theme_mode}
            options={withCurrentValue([...selectOptions.theme_mode], value.theme_mode)}
            onChange={(next) => onChange({ ...value, theme_mode: next })}
          />
          <Select
            label="Cor de destaque"
            description="Define a cor principal usada em botões e elementos ativos."
            value={value.accent_color}
            options={withCurrentValue([...selectOptions.accent_color], value.accent_color)}
            onChange={(next) => onChange({ ...value, accent_color: next })}
          />
        </Card>

        <Card title="Idioma e Voz" subtitle="Escolha o idioma da interface e a forma de comunicacao da experiencia.">
          <Select
            label="Idioma"
            description="Seleciona o idioma principal da interface."
            value={value.language}
            options={withCurrentValue([...selectOptions.language], value.language)}
            onChange={(next) => onChange({ ...value, language: next })}
          />
          <Select
            label="Voz"
            description="Define o estilo de voz usado pela experiência da plataforma."
            value={value.voice}
            options={withCurrentValue([...selectOptions.voice], value.voice)}
            onChange={(next) => onChange({ ...value, voice: next })}
          />
        </Card>

        <Card title="Experiência" subtitle="Controle como a plataforma responde e interage com você no uso diario.">
          <Toggle
            label="Autocompletar respostas"
            description="Sugere continuações enquanto você escreve ou interage."
            checked={value.autocomplete}
            onChange={(next) => onChange({ ...value, autocomplete: next })}
          />
          <Toggle
            label="Conversas em segundo plano"
            description="Permite manter atividades rodando enquanto você navega em outras áreas."
            checked={value.background_conversation}
            onChange={(next) => onChange({ ...value, background_conversation: next })}
          />
          <Toggle
            label="Feedback tátil"
            description="Ativa respostas de toque em dispositivos compatíveis."
            checked={value.haptic_feedback}
            onChange={(next) => onChange({ ...value, haptic_feedback: next })}
          />
        </Card>

        <Card title="Interface" subtitle="Organize como os conteudos e areas da plataforma aparecem na tela.">
          <Toggle
            label="Modo dividido"
            description="Permite trabalhar com mais de uma área ou conversa lado a lado."
            checked={value.split_mode}
            onChange={(next) => onChange({ ...value, split_mode: next })}
          />
          <Toggle
            label="Resposta em sequência"
            description="Mantém o fluxo de respostas organizado em sequência automática."
            checked={value.sequence}
            onChange={(next) => onChange({ ...value, sequence: next })}
          />
          <Toggle
            label="Mostrar conteúdos em alta"
            description="Exibe sugestões e tendências relevantes na interface."
            checked={value.trending}
            onChange={(next) => onChange({ ...value, trending: next })}
          />
        </Card>
      </div>

      <div className="mt-10 flex flex-col items-end gap-3">
        {saveStatus !== 'idle' && saveMessage ? (
          <p className={`text-sm ${saveStatus === 'success' ? 'text-emerald-300' : 'text-rose-300'}`}>{saveMessage}</p>
        ) : null}
        <button
          type="button"
          onClick={onSave}
          disabled={saving}
          className="inline-flex min-w-[220px] items-center justify-center rounded-2xl bg-cyan px-8 py-3.5 text-base font-semibold text-ink transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {saving ? (
            <span className="inline-flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-ink/30 border-t-ink" />
              Salvando alterações...
            </span>
          ) : (
            'Salvar alterações'
          )}
        </button>
      </div>
    </section>
  );
}
