import { Bot, Check, Monitor, Palette, Sparkles, Zap } from 'lucide-react';

import { ThemePreview } from './ThemePreview';
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
  eyebrow: string;
  title: string;
  description: string;
  icon: React.ElementType;
  children: React.ReactNode;
}

interface Choice {
  label: string;
  value: string;
  description?: string;
}

const themeChoices: Choice[] = [
  { label: 'Dark', value: 'dark', description: 'Classico AXI' },
  { label: 'Dark Premium', value: 'dark-premium', description: 'Mais contraste' },
  { label: 'Midnight', value: 'midnight', description: 'Foco noturno' },
  { label: 'Ocean', value: 'ocean', description: 'Azul profundo' },
  { label: 'Executive', value: 'executive', description: 'Sutil e direto' },
];

const accentChoices: Choice[] = [
  { label: 'Roxo AXI', value: 'axi' },
  { label: 'Azul', value: 'blue' },
  { label: 'Ciano', value: 'cyan' },
  { label: 'Verde', value: 'green' },
  { label: 'Dourado', value: 'gold' },
];

const languageChoices: Choice[] = [
  { label: 'Portugues Brasil', value: 'pt-BR' },
  { label: 'English', value: 'en-US' },
  { label: 'Espanol', value: 'es-ES' },
];

const assistantModeChoices: Choice[] = [
  { label: 'Executivo', value: 'executivo' },
  { label: 'Operacional', value: 'operacional' },
  { label: 'Marketing', value: 'marketing' },
  { label: 'Criativo', value: 'criativo' },
  { label: 'Automatico', value: 'automatico' },
];

const responseDetailChoices: Choice[] = [
  { label: 'Curtas', value: 'curtas' },
  { label: 'Normais', value: 'normais' },
  { label: 'Detalhadas', value: 'detalhadas' },
];

const toneChoices: Choice[] = [
  { label: 'Profissional', value: 'profissional' },
  { label: 'Amigavel', value: 'amigavel' },
  { label: 'Tecnico', value: 'tecnico' },
];

function Card({ eyebrow, title, description, icon: Icon, children }: CardProps) {
  return (
    <section className="rounded-[1.4rem] border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.84),rgba(2,6,23,0.66))] p-5 shadow-[0_22px_70px_rgba(0,0,0,0.26)]">
      <div className="mb-5 flex items-start gap-4">
        <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-violet-500/15 text-violet-200">
          <Icon size={22} />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-violet-300">{eyebrow}</p>
          <h3 className="mt-1 font-display text-2xl text-white">{title}</h3>
          <p className="mt-1 text-sm leading-6 text-slate-400">{description}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function ChoiceGrid({
  label,
  choices,
  value,
  onChange,
}: {
  label: string;
  choices: Choice[];
  value: string;
  onChange: (next: string) => void;
}) {
  return (
    <div>
      <p className="mb-3 text-sm font-semibold text-slate-200">{label}</p>
      <div className="grid gap-2 sm:grid-cols-2 xl:grid-cols-3">
        {choices.map((choice) => {
          const active = choice.value === value;
          return (
            <button
              key={choice.value}
              type="button"
              onClick={() => onChange(choice.value)}
              className={[
                'min-h-[74px] rounded-2xl border p-3 text-left transition duration-200',
                active ? 'border-violet-300/60 bg-violet-500/16 text-white shadow-[0_16px_36px_rgba(124,58,237,0.18)]' : 'border-white/10 bg-white/[0.035] text-slate-300 hover:border-violet-300/35 hover:bg-white/[0.055]',
              ].join(' ')}
            >
              <span className="flex items-center justify-between gap-3">
                <span className="font-semibold">{choice.label}</span>
                {active ? <Check size={16} className="text-violet-200" /> : null}
              </span>
              {choice.description ? <span className="mt-1 block text-xs text-slate-500">{choice.description}</span> : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <label className="group flex cursor-pointer items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.035] p-4 transition hover:border-violet-300/30 hover:bg-white/[0.055]">
      <span>
        <span className="block text-sm font-semibold text-white">{label}</span>
        <span className="mt-1 block text-xs leading-5 text-slate-400">{description}</span>
      </span>
      <span className="relative inline-flex h-7 w-12 shrink-0">
        <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} className="peer sr-only" />
        <span className="absolute inset-0 rounded-full bg-slate-700 transition peer-checked:bg-violet-600 peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-violet-300" />
        <span className="absolute left-1 top-1 h-5 w-5 rounded-full bg-white transition peer-checked:translate-x-5" />
      </span>
    </label>
  );
}

export function PreferencesForm({ value, onChange, onSave, saving, saveStatus = 'idle', saveMessage }: PreferencesFormProps) {
  return (
    <section className="rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_12%_0%,rgba(124,58,237,0.18),transparent_32%),#050914] p-5 text-white shadow-[0_28px_100px_rgba(0,0,0,0.42)] md:p-7">
      <header className="mb-7 flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-violet-300">Preferencias</p>
          <h2 className="mt-2 font-display text-4xl text-white">Central de experiencia</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
            Personalize a AXI como um cockpit premium: aparencia, idioma, produtividade e comportamento do AXI Assistant.
          </p>
        </div>
        <div className="rounded-2xl border border-emerald-300/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
          Aplicacao imediata na interface
        </div>
      </header>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
        <div className="space-y-5">
          <Card eyebrow="Aparencia" title="Tema e identidade visual" description="Escolha o clima visual da plataforma e a cor principal dos estados ativos." icon={Palette}>
            <div className="space-y-5">
              <ChoiceGrid label="Tema" choices={themeChoices} value={value.theme_mode} onChange={(next) => onChange({ ...value, theme_mode: next })} />
              <ChoiceGrid label="Cor principal" choices={accentChoices} value={value.accent_color} onChange={(next) => onChange({ ...value, accent_color: next })} />
            </div>
          </Card>

          <Card eyebrow="Idioma" title="Idioma da experiencia" description="Defina como a interface se comunica com voce." icon={Monitor}>
            <ChoiceGrid label="Idioma" choices={languageChoices} value={value.language} onChange={(next) => onChange({ ...value, language: next })} />
          </Card>

          <Card eyebrow="Experiencia" title="Sensacao de uso" description="Controle movimento, dicas e protecoes durante operacoes importantes." icon={Sparkles}>
            <div className="grid gap-3">
              <ToggleRow label="Animacoes da interface" description="Transicoes suaves entre cards, menus e estados." checked={value.interface_animations} onChange={(next) => onChange({ ...value, interface_animations: next })} />
              <ToggleRow label="Efeitos visuais avancados" description="Glass, gradientes e brilho contextual quando fizer sentido." checked={value.advanced_visual_effects} onChange={(next) => onChange({ ...value, advanced_visual_effects: next })} />
              <ToggleRow label="Compactar menus" description="Reduz densidade lateral para trabalhar com mais espaco." checked={value.compact_menus} onChange={(next) => onChange({ ...value, compact_menus: next })} />
              <ToggleRow label="Exibir dicas contextuais" description="Mostra orientacoes curtas em fluxos novos ou sensiveis." checked={value.contextual_tips} onChange={(next) => onChange({ ...value, contextual_tips: next })} />
              <ToggleRow label="Confirmar acoes criticas" description="Pede confirmacao antes de apagar, exportar ou alterar dados sensiveis." checked={value.confirm_critical_actions} onChange={(next) => onChange({ ...value, confirm_critical_actions: next })} />
            </div>
          </Card>
        </div>

        <div className="space-y-5">
          <ThemePreview accentColor={value.accent_color} themeMode={value.theme_mode} />

          <Card eyebrow="Produtividade" title="Rotina mais rapida" description="Preferencias para voltar ao trabalho sem reorganizar tudo manualmente." icon={Zap}>
            <div className="grid gap-3">
              <ToggleRow label="Abrir ultimo modulo utilizado" description="Retorna ao ultimo contexto apos login." checked={value.open_last_module} onChange={(next) => onChange({ ...value, open_last_module: next })} />
              <ToggleRow label="Salvar filtros automaticamente" description="Mantem filtros de Revenue, Marketing e Chats por usuario." checked={value.autosave_filters} onChange={(next) => onChange({ ...value, autosave_filters: next })} />
              <ToggleRow label="Ativar atalhos de teclado" description="Permite comandos rapidos para navegacao e acoes frequentes." checked={value.keyboard_shortcuts} onChange={(next) => onChange({ ...value, keyboard_shortcuts: next })} />
              <ToggleRow label="Mostrar metricas rapidas na Home" description="Exibe resumo executivo assim que voce entra." checked={value.show_quick_metrics} onChange={(next) => onChange({ ...value, show_quick_metrics: next })} />
            </div>
          </Card>

          <Card eyebrow="AXI Assistant" title="Comportamento do assistente" description="Ajuste como o assistente pensa, responde e se adapta ao seu trabalho." icon={Bot}>
            <div className="space-y-5">
              <ChoiceGrid label="Modo do assistente" choices={assistantModeChoices} value={value.assistant_mode} onChange={(next) => onChange({ ...value, assistant_mode: next })} />
              <ChoiceGrid label="Configuracao de respostas" choices={responseDetailChoices} value={value.assistant_response_detail} onChange={(next) => onChange({ ...value, assistant_response_detail: next })} />
              <ChoiceGrid label="Tom de comunicacao" choices={toneChoices} value={value.assistant_tone} onChange={(next) => onChange({ ...value, assistant_tone: next })} />
            </div>
          </Card>
        </div>
      </div>

      <div className="mt-7 flex flex-col gap-3 border-t border-white/10 pt-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold text-white">Preferencias salvas por usuario</p>
          <p className="mt-1 text-xs text-slate-500">As alteracoes sao persistidas no banco e reaplicadas automaticamente apos login.</p>
        </div>
        <div className="flex flex-col items-end gap-3">
          {saveStatus !== 'idle' && saveMessage ? (
            <p className={`text-sm ${saveStatus === 'success' ? 'text-emerald-300' : 'text-rose-300'}`}>{saveMessage}</p>
          ) : null}
          <button
            type="button"
            onClick={onSave}
            disabled={saving}
            className="inline-flex min-w-[220px] items-center justify-center rounded-2xl bg-violet-600 px-8 py-3.5 text-base font-semibold text-white transition hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {saving ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                Salvando...
              </span>
            ) : (
              'Salvar preferencias'
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
