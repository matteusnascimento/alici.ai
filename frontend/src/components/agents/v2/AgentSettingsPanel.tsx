import type { AgentSettings } from '../../../types/agentsV2';

interface AgentSettingsPanelProps {
  settings: AgentSettings;
  onChange: (next: AgentSettings) => void;
  onSave: () => void;
  saving: boolean;
}

function SettingsBlock({ label, description, children }: { label: string; description?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
      <div className="mb-4 border-b border-white/8 pb-4">
        <h2 className="font-display text-lg font-semibold text-white">{label}</h2>
        {description ? <p className="mt-0.5 text-sm text-slate-400">{description}</p> : null}
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="block text-xs font-medium uppercase tracking-[0.15em] text-slate-400">{label}</label>
      {children}
    </div>
  );
}

const inputClass = 'w-full rounded-xl border border-white/10 bg-black/30 px-3.5 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-cyan/50 focus:outline-none focus:ring-1 focus:ring-cyan/30 transition';

const PROMPT_TEMPLATES = [
  'Você é um atendente virtual especializado em responder clientes com clareza, objetividade e foco em conversão.',
  'Você é um agente comercial que qualifica leads, identifica intenção de compra e conduz para fechamento com linguagem consultiva.',
  'Você é um operador de suporte que resolve dúvidas rapidamente, reduz atrito e direciona para humanos quando necessário.',
];

export function AgentSettingsPanel({ settings, onChange, onSave, saving }: AgentSettingsPanelProps) {
  const setBasic = (patch: Partial<typeof settings.basic>) =>
    onChange({ ...settings, basic: { ...settings.basic, ...patch } });

  const setAdvanced = (patch: Partial<typeof settings.advanced>) =>
    onChange({ ...settings, advanced: { ...settings.advanced, ...patch } });

  const agentStatus = settings.advanced.status || 'ativo';
  const isActive = agentStatus === 'ativo';
  const promptValue = settings.advanced.instrucoes_principais_do_agente || '';
  const temperatureValue = Number(settings.advanced.temperature || '0.7');
  const normalizedTemperature = Number.isNaN(temperatureValue) ? 0.7 : Math.min(1, Math.max(0, temperatureValue));

  function applyPromptTemplate(index: number) {
    setAdvanced({ instrucoes_principais_do_agente: PROMPT_TEMPLATES[index] });
  }

  function generatePromptSuggestion() {
    const role = settings.basic.role?.trim() || 'atendimento e vendas';
    const language = settings.basic.language?.trim() || 'pt-BR';
    const tone = settings.basic.tone?.trim() || 'profissional e objetivo';

    setAdvanced({
      instrucoes_principais_do_agente: `Você é um agente de IA focado em ${role}. Responda sempre em ${language}, com tom ${tone}. Priorize clareza, ação e conversão. Faça perguntas curtas para avançar a conversa e, quando necessário, direcione para humano com contexto resumido.`,
    });
  }

  return (
    <div className="space-y-5">
      <section className={`rounded-3xl border p-5 ${isActive ? 'border-emerald-400/30 bg-emerald-500/10' : 'border-amber-400/30 bg-amber-500/10'}`}>
        <p className="text-[10px] uppercase tracking-[0.2em] text-slate-300">Status do agente</p>
        <p className="mt-2 text-sm font-semibold text-white">
          {isActive ? '● Ativo e respondendo clientes' : '● Inativo (não está operando)'}
        </p>
      </section>

      <SettingsBlock label="1. Identidade" description="Defina quem é o agente e como ele se apresenta.">
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Nome do agente">
            <input
              value={settings.basic.name}
              onChange={(e) => setBasic({ name: e.target.value })}
              placeholder="Ex: Atendente Virtual"
              className={inputClass}
            />
          </Field>
          <Field label="Função / Cargo">
            <input
              value={settings.basic.role}
              onChange={(e) => setBasic({ role: e.target.value })}
              placeholder="Ex: Suporte ao cliente"
              className={inputClass}
            />
          </Field>
          <Field label="Idioma padrão">
            <input
              value={settings.basic.language}
              onChange={(e) => setBasic({ language: e.target.value })}
              placeholder="Ex: pt-BR"
              className={inputClass}
            />
          </Field>
          <Field label="Tom de voz">
            <input
              value={settings.basic.tone || ''}
              onChange={(e) => setBasic({ tone: e.target.value })}
              placeholder="Ex: Amigável e objetivo"
              className={inputClass}
            />
          </Field>
        </div>
      </SettingsBlock>

      <SettingsBlock label="2. Cérebro da IA" description="Defina como o agente pensa, responde e conduz conversas.">
        <Field label="🧠 Instruções da IA (System Prompt)">
          <textarea
            value={promptValue}
            onChange={(e) => setAdvanced({ instrucoes_principais_do_agente: e.target.value })}
            placeholder="Ex: Você é um atendente virtual especializado em responder clientes com foco em rapidez, clareza e conversão..."
            rows={9}
            className={`${inputClass} resize-y`}
          />
        </Field>

        {promptValue.trim().length === 0 ? (
          <div className="rounded-2xl border border-cyan/20 bg-cyan/5 px-4 py-3 text-sm text-slate-200">
            Sugestão: “Você é um atendente virtual especializado em responder clientes de forma clara, empática e orientada à conversão.”
          </div>
        ) : null}

        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={generatePromptSuggestion}
            className="rounded-xl border border-cyan/35 bg-cyan/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.1em] text-cyan transition hover:bg-cyan/20"
          >
            Gerar sugestão com IA
          </button>
          {PROMPT_TEMPLATES.map((_, index) => (
            <button
              key={index}
              type="button"
              onClick={() => applyPromptTemplate(index)}
              className="rounded-xl border border-white/15 bg-white/[0.03] px-3 py-2 text-xs font-semibold uppercase tracking-[0.1em] text-slate-200 transition hover:border-white/25"
            >
              Usar template {index + 1}
            </button>
          ))}
        </div>
      </SettingsBlock>

      <SettingsBlock label="3. Configuração da IA" description="Ajuste modelo e nível de criatividade das respostas.">
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Modelo de IA">
            <input
              value={settings.advanced.modelo || ''}
              onChange={(e) => setAdvanced({ modelo: e.target.value })}
              placeholder="Ex: gpt-4o-mini"
              className={inputClass}
            />
          </Field>

          <Field label="Criatividade (temperatura)">
            <div className="rounded-xl border border-white/10 bg-black/20 px-3 py-3">
              <div className="mb-2 flex items-center justify-between text-xs text-slate-300">
                <span>Mais previsível</span>
                <span className="font-semibold text-cyan">{normalizedTemperature.toFixed(1)}</span>
                <span>Mais criativo</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={normalizedTemperature}
                onChange={(e) => setAdvanced({ temperature: e.target.value })}
                className="w-full accent-cyan"
              />
            </div>
          </Field>
        </div>
      </SettingsBlock>

      <SettingsBlock label="4. Operação" description="Defina como o agente trabalha no dia a dia da operação.">
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Status">
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAdvanced({ status: 'ativo' })}
                className={`rounded-xl border px-3 py-2 text-sm transition ${
                  (settings.advanced.status || 'ativo') === 'ativo'
                    ? 'border-emerald-400/40 bg-emerald-500/15 text-emerald-200'
                    : 'border-white/10 bg-white/[0.03] text-slate-200'
                }`}
              >
                Ativo
              </button>
              <button
                type="button"
                onClick={() => setAdvanced({ status: 'pausado' })}
                className={`rounded-xl border px-3 py-2 text-sm transition ${
                  settings.advanced.status === 'pausado'
                    ? 'border-amber-400/40 bg-amber-500/15 text-amber-200'
                    : 'border-white/10 bg-white/[0.03] text-slate-200'
                }`}
              >
                Pausado
              </button>
            </div>
          </Field>

          <Field label="Modo de resposta">
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setAdvanced({ modo_resposta: 'automatico' })}
                className={`rounded-xl border px-3 py-2 text-sm transition ${
                  (settings.advanced.modo_resposta || 'automatico') === 'automatico'
                    ? 'border-cyan/45 bg-cyan/12 text-cyan'
                    : 'border-white/10 bg-white/[0.03] text-slate-200'
                }`}
              >
                Automático
              </button>
              <button
                type="button"
                onClick={() => setAdvanced({ modo_resposta: 'supervisionado' })}
                className={`rounded-xl border px-3 py-2 text-sm transition ${
                  settings.advanced.modo_resposta === 'supervisionado'
                    ? 'border-cyan/45 bg-cyan/12 text-cyan'
                    : 'border-white/10 bg-white/[0.03] text-slate-200'
                }`}
              >
                Assistido
              </button>
            </div>
          </Field>
        </div>
      </SettingsBlock>

      <SettingsBlock label="5. Segurança" description="Defina o nível de controle e restrição do agente.">
        <div className="grid gap-4 md:grid-cols-2">
          <Field label="Nível de controle">
            <input
              value={settings.advanced.nivel_auditoria || 'basico'}
              onChange={(e) => setAdvanced({ nivel_auditoria: e.target.value })}
              placeholder="Básico, Moderado ou Restrito"
              className={inputClass}
            />
          </Field>

          <Field label="Restrições de conteúdo">
            <select
              value={settings.advanced.restricoes_conteudo || 'padrao'}
              onChange={(e) => setAdvanced({ restricoes_conteudo: e.target.value })}
              className={inputClass}
            >
              <option value="padrao">Padrão</option>
              <option value="moderado">Moderado</option>
              <option value="restrito">Restrito</option>
            </select>
          </Field>
        </div>

        <div className="rounded-2xl border border-slate-600/30 bg-black/20 px-4 py-3 text-xs text-slate-400">
          Credenciais e tokens ficam protegidos no backend. Use nível moderado ou restrito para operações sensíveis.
        </div>
      </SettingsBlock>

      <div className="flex justify-end pb-2">
        <button
          type="button"
          onClick={onSave}
          disabled={saving}
          className="rounded-2xl bg-cyan px-6 py-2.5 text-sm font-semibold text-ink transition hover:brightness-110 disabled:opacity-50"
        >
          {saving ? 'Salvando...' : 'Salvar configurações'}
        </button>
      </div>
    </div>
  );
}

