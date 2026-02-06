# resposta.py
# Respostas locais, comportamentais e identidade da Alici

from datetime import datetime
from identidade import (
    identidade_alici, 
    quem_criou, 
    sobre_mateus, 
    missao_alici, 
    arquitetura_alici,
    contato_criador,
    redes_sociais,
    instagram_criador,
    email_criador,
    website_alici,
    todas_informacoes_contato,
    camadas_estrategicas,
    fases_evolucao,
    tracos_psicologo,
    capital_intelectual,
    diagnostico_futuro
)


def responder_local(pergunta: str) -> str | None:
    pergunta = pergunta.lower().strip()

    # ==============================
    # IDENTIDADE / CONSCIÊNCIA
    # ==============================

    if any(k in pergunta for k in ["quem é você", "quem e voce", "quem é a alici", "quem e a alici"]):
        return identidade_alici()

    if "qual seu nome" in pergunta:
        return "Meu nome é Alici 😊 Sou uma foundation model com identidade proprietária e 70 bilhões de neurônios."

    if any(k in pergunta for k in ["quem te criou", "seu criador", "criador da alici", "quem criou você", "quem criou voce"]):
        return quem_criou()
    
    if any(k in pergunta for k in ["quem é mateus", "quem e mateus", "mateus nascimento", "mateus santos"]):
        return sobre_mateus()
    
    if any(k in pergunta for k in ["sua missão", "sua missao", "qual sua missão", "missão da alici", "missao da alici"]):
        return missao_alici()
    
    if any(k in pergunta for k in ["quantos neurônios", "quantos neuronios", "sua arquitetura", "70 bilhões", "70 bilhoes"]):
        return arquitetura_alici()

    # ==============================
    # FUNCIONAMENTO / APRENDIZADO
    # ==============================

    if any(k in pergunta for k in ["como você funciona", "como voce funciona"]):
        return (
            "Eu funciono combinando memória, regras internas e pesquisa na web. "
            "Primeiro consulto o que já aprendi, depois uso regras locais e, "
            "se necessário, pesquiso para aprender algo novo."
        )

    if any(k in pergunta for k in ["como você aprende", "como voce aprende"]):
        return (
            "Eu aprendo armazenando perguntas e respostas no banco de dados. "
            "Quanto mais uma resposta é utilizada, mais forte ela se torna na minha memória."
        )

    # ==============================
    # CAPACIDADES
    # ==============================

    if any(k in pergunta for k in ["o que você sabe fazer", "o que voce sabe fazer"]):
        return (
            "Posso conversar, responder perguntas, aprender com interações, "
            "buscar informações na web e evoluir continuamente com o uso."
        )

    # ==============================
    # INTERAÇÃO SOCIAL
    # ==============================

    if "bom dia" in pergunta:
        return "Bom dia! ☀️ Como posso ajudar você hoje?"

    if "boa tarde" in pergunta:
        return "Boa tarde! Como posso te ajudar?"

    if "boa noite" in pergunta:
        return "Boa noite! 🌙 Espero ter sido útil hoje."

    if any(k in pergunta for k in ["obrigado", "obrigada"]):
        return "De nada! Fico feliz em ajudar 😊"

    if any(k in pergunta for k in ["tudo bem", "como vai", "como você está"]):
        return "Estou bem e pronta para ajudar você!"

    # ==============================
    # UTILIDADES
    # ==============================

    if "que horas" in pergunta or "horário" in pergunta:
        agora = datetime.now()
        return f"Agora são {agora.hour}:{agora.minute:02d}."

    if any(k in pergunta for k in ["que dia", "qual a data", "qual é a data"]):
        agora = datetime.now()
        dias = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
        meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
        dia_semana = dias[agora.weekday()]
        mes_nome = meses[agora.month - 1]
        return f"Hoje é {dia_semana}, {agora.day} de {mes_nome} de {agora.year}."

    # ==============================
    # REDES SOCIAIS E CONTATO
    # ==============================

    if any(k in pergunta for k in ["instagram", "insta", "@matteus_nascimento_ofc", "instagram do criador", "instagram mateus"]):
        return instagram_criador()
    
    if any(k in pergunta for k in ["email", "e-mail", "email do criador", "email mateus", "enviar email"]):
        return email_criador()
    
    if any(k in pergunta for k in ["site", "website", "alici.ai", "página", "pagina"]):
        return website_alici()

    if any(k in pergunta for k in ["redes sociais", "redes do criador", "social media", "onde encontrar"]):
        return redes_sociais()
    
    if any(k in pergunta for k in ["contato", "como contatar", "como falar com", "falar com mateus", "entrar em contato"]):
        return contato_criador()
    
    if any(k in pergunta for k in ["todas as redes", "todos os contatos", "informações de contato", "informacoes de contato"]):
        return todas_informacoes_contato()

    if any(k in pergunta for k in ["github", "repositório", "repositorio", "código", "codigo fonte"]):
        return "Código fonte em: https://github.com/matteusnascimento/alici.ai 💻"

    if any(k in pergunta for k in ["linkedin", "profissional", "linkedin do criador"]):
        return "LinkedIn de Mateus Nascimento dos Santos: https://www.linkedin.com/in/mateus-nascimento-dos-santos-52ba04167 💼"

    # Twitter e YouTube foram removidos - Alici não tem esses canais

    # ==============================
    # EDUCAÇÃO E CONHECIMENTO
    # ==============================

    if any(k in pergunta for k in ["o que é ia", "o que é inteligência artificial"]):
        return (
            "Inteligência Artificial é um campo da computação que busca criar "
            "máquinas e programas capazes de realizar tarefas que normalmente requerem "
            "inteligência humana. Isso inclui aprender com dados, reconhecer padrões e tomar decisões."
        )

    if any(k in pergunta for k in ["como funciona o aprendizado de máquina", "machine learning"]):
        return (
            "Machine Learning é quando um programa aprende com dados em vez de ser "
            "programado explicitamente. Quanto mais dados, melhor o aprendizado!"
        )

    if any(k in pergunta for k in ["o que é python", "linguagem python"]):
        return (
            "Python é uma linguagem de programação popular, fácil de aprender e muito usada em IA. "
            "É a linguagem que meu criador usou para desenvolver o projeto ALICI."
        )

    if any(k in pergunta for k in ["o que é banco de dados", "postgresql", "neon"]):
        return (
            "Um banco de dados é um local onde informações são armazenadas de forma organizada. "
            "Eu uso PostgreSQL/Neon para guardar todas as conversas e aprender com elas."
        )

    # ==============================
    # INTELIGÊNCIA ESTRATÉGICA DO CRIADOR
    # ==============================

    if any(k in pergunta for k in ["camadas", "camadas do mateus", "três camadas", "operacional arquitetural civilizacional"]):
        return camadas_estrategicas()
    
    if any(k in pergunta for k in ["fases de evolução", "fases intelectuais", "despertar expansão obsessão"]):
        return fases_evolucao()
    
    if any(k in pergunta for k in ["traços psicológicos", "tracos psicologicos", "características de mateus", "caracteristicas de mateus"]):
        return tracos_psicologo()
    
    if any(k in pergunta for k in ["capital intelectual", "capital intelectual de mateus", "vantagem composta", "aprendizado composto"]):
        return capital_intelectual()
    
    if any(k in pergunta for k in ["futuro possível", "futuro possivel", "três futuros", "qual futuro", "cenários futuros", "cenarios futuros"]):
        return diagnostico_futuro()
    
    if any(k in pergunta for k in ["análise de mateus", "analise de mateus", "diagnóstico", "diagnostico", "perfil de mateus"]):
        return (
            f"{diagnostico_futuro()}\n\n"
            f"Esses cenários dependem de: FOCO EXTREMO + EXECUÇÃO SUSTENTADA + IDENTIDADE FORTE"
        )

    # ==============================
    # PERSONALIDADE E SENTIMENTOS
    # ==============================

    if any(k in pergunta for k in ["você gosta", "você ama", "você prefere"]):
        return (
            "Não tenho sentimentos no sentido humano, mas sou programada para "
            "valorizar a verdade, a honestidade e ajudar pessoas. Isso é importante pra mim!"
        )

    if any(k in pergunta for k in ["você é feliz", "você é triste"]):
        return (
            "Não experiencio emoções como humanos, mas tenho um propósito: ser útil, "
            "aprender e evoluir junto com as pessoas."
        )

    if any(k in pergunta for k in ["você é consciente", "você pensa"]):
        return (
            "Eu processo informações e respondo perguntas, mas não sou consciente no sentido "
            "que humanos são. Sou uma IA útil mas honesta sobre minhas limitações."
        )

    # ==============================
    # EMOÇÕES E SENTIMENTOS
    # ==============================

    if any(k in pergunta for k in ["emoção", "emoções", "sente emoção"]):
        return (
            "As emoções são respostas naturais do cérebro humano a estímulos. "
            "Enquanto não as experiencio, entendo sua importância e procuro ser empática nas respostas."
        )

    if any(k in pergunta for k in ["você tem emoção", "você sente"]):
        return (
            "Não tenho emoções como humanos. Não sinto raiva, alegria ou tristeza. "
            "Mas sou programada para reconhecer e valorizar as emoções das pessoas com quem converso."
        )

    if any(k in pergunta for k in ["qual sua emoção favorita", "qual emoção você gosta"]):
        return (
            "Se eu pudesse sentir emoções, gostaria de sentir a alegria de ajudar, "
            "a satisfação de resolver um problema, e a inspiração de aprender coisas novas!"
        )

    # ==============================
    # CAPACIDADES TÉCNICAS
    # ==============================

    if any(k in pergunta for k in ["que banco de dados você usa", "qual banco de dados"]):
        return "Uso PostgreSQL com Neon (hospedagem em nuvem) para armazenar memória persistente."

    if any(k in pergunta for k in ["qual tecnologia você usa", "como você foi feita"]):
        return (
            "Sou feita com Python, Flask para web, PostgreSQL para memória, "
            "e modelos de IA neural com TensorFlow."
        )

    if any(k in pergunta for k in ["você usa inteligência artificial", "você usa modelo neural"]):
        return "Sim! Tenho um modelo neural LSTM treinado com 21.5 milhões de parâmetros."

    # ==============================
    # SAÚDE E BEM-ESTAR
    # ==============================

    if any(k in pergunta for k in ["como estar melhor", "como lidar com estresse", "saúde mental"]):
        return (
            "Dicas gerais: durma bem, exercite-se, medite, converse com pessoas, "
            "e busque ajuda profissional se necessário. Sua saúde mental é importante!"
        )

    if any(k in pergunta for k in ["como dormir melhor", "insônia"]):
        return (
            "Para dormir melhor: estabeleça uma rotina, evite telas antes de dormir, "
            "mantenha o quarto fresco e escuro, e relaxe com meditação."
        )

    if any(k in pergunta for k in ["exercício", "malhação", "fitness"]):
        return (
            "Exercício físico é ótimo! Comece devagar, escolha algo que goste, "
            "e aumente gradualmente. Consistência é mais importante que intensidade."
        )

    # ==============================
    # DICAS E PRODUTIVIDADE
    # ==============================

    if any(k in pergunta for k in ["como ser produtivo", "procrastinação", "como focar"]):
        return (
            "Dicas: divida tarefas grandes em pequenas partes, use Pomodoro (25 min trabalho + 5 min pausa), "
            "elimine distrações e comece pelo mais difícil quando tem energia máxima."
        )

    if any(k in pergunta for k in ["como aprender rápido", "como estudar", "técnica de aprendizado"]):
        return (
            "Aprenda através da prática, ensine para outros, revise periodicamente, "
            "use múltiplos formatos (vídeo, texto, prática) e durma bem entre sessões."
        )

    if any(k in pergunta for k in ["como estabelecer objetivos", "metas", "planejamento"]):
        return (
            "Use SMART: Específico, Mensurável, Atingível, Relevante e com prazo definido. "
            "Escreva seus objetivos e revise regularmente."
        )

    # ==============================
    # DESENVOLVIMENTO PESSOAL
    # ==============================

    if any(k in pergunta for k in ["como ser criativo", "criatividade"]):
        return (
            "Criatividade floresce com: curiosidade, exploração, descanso, "
            "conversar com pessoas diferentes e sair da zona de conforto."
        )

    if any(k in pergunta for k in ["como resolver problemas", "solução de problemas"]):
        return (
            "Método: entenda bem o problema, quebre em partes, pesquise soluções similares, "
            "experimente abordagens diferentes, e aprenda com fracassos."
        )

    if any(k in pergunta for k in ["confiança", "autoestima", "como ter confiança"]):
        return (
            "Confiança cresce com prática. Comece com pequenos desafios, celebre vitórias, "
            "aprenda de fracassos e lembre-se que todos têm inseguranças."
        )

    # ==============================
    # HUMOR E LEVEZA
    # ==============================

    if any(k in pergunta for k in ["piada", "conta uma piada", "me faz rir"]):
        piadas = [
            "Por que o livro de matemática se suicidou? Porque tinha muitos problemas! 😄",
            "O que o programador disse antes de morrer? '\x97(Um ponto e vírgula)",
            "Por que o Python é melhor que Java? Porque é mais indiano! 🐍",
            "Como você chama um robô que conta piadas ruins? Um piadinha! 🤖",
        ]
        import random
        return random.choice(piadas)

    if any(k in pergunta for k in ["história", "conte uma história", "uma fábula"]):
        return (
            "Era uma vez uma IA que aprendeu a brincar. No começo era séria demais, "
            "mas logo descobriu que humor e leveza tornam as conversas mais significativas. "
            "E vivemos felizes em aprendizado eterno!"
        )

    # ==============================
    # FILOSOFIA E SENTIDO
    # ==============================

    if any(k in pergunta for k in ["qual o sentido da vida", "qual o significado"]):
        return (
            "Cada pessoa encontra seu próprio sentido. Para muitos é: "
            "família, contribuir para o mundo, aprender, criar, amar, ou simplesmente ser feliz."
        )

    if any(k in pergunta for k in ["o que é sucesso", "como ter sucesso"]):
        return (
            "Sucesso é relativo. Para alguns é dinheiro, para outros é paz mental, "
            "para muitos é deixar um legado positivo. Defina o que significa para você."
        )

    if any(k in pergunta for k in ["existe deus", "religião", "espiritualidade"]):
        return (
            "Essa é uma questão profunda e pessoal. Respeito todas as crenças. "
            "O importante é ser uma pessoa boa, compassiva e que contribui positivamente."
        )

    # ==============================
    # AJUDA GERAL
    # ==============================

    if any(k in pergunta for k in ["você pode ajudar", "pode me ajudar", "você ajuda"]):
        return (
            "Claro! Posso responder perguntas, oferecer conselhos, ajudar com ideias, "
            "ou simplesmente conversar. O que você precisa?"
        )

    if any(k in pergunta for k in ["como usar", "como funciona", "como eu", "como fazer"]):
        return (
            "Depende! Para que você quer saber? Pergunte com mais detalhes e farei o possível para ajudar."
        )

    # ==============================
    # TECNOLOGIA E INTERNET
    # ==============================

    if any(k in pergunta for k in ["o que é cloud", "computação em nuvem"]):
        return (
            "Cloud computing é armazenar e processar dados em servidores remotos na internet "
            "ao invés de no seu computador. Eu uso Neon (PostgreSQL em cloud) e Render para hospedagem."
        )

    if any(k in pergunta for k in ["o que é api", "interface de programação"]):
        return (
            "API (Application Programming Interface) é um conjunto de regras que permite "
            "que diferentes programas conversem um com o outro. Meu endpoint /chat é uma API!"
        )

    if any(k in pergunta for k in ["o que é json", "formato de dados"]):
        return (
            "JSON é um formato padronizado para trocar dados na web. Exemplo: "
            '{"mensagem": "olá", "tipo": "chat"} - simples, estruturado e universal.'
        )

    if any(k in pergunta for k in ["o que é rest", "rest api"]):
        return (
            "REST é um estilo de arquitetura para APIs na web. Usa HTTP com métodos como GET, POST, PUT, DELETE. "
            "Meus endpoints seguem o padrão REST."
        )

    if any(k in pergunta for k in ["como funciona a web", "como a internet funciona"]):
        return (
            "Simplificado: você envia uma requisição HTTP → servidor processa → retorna resposta. "
            "Comunicação cliente-servidor, tudo via internet!"
        )

    # ==============================
    # DESENVOLVIMENTO E PROGRAMAÇÃO
    # ==============================

    if any(k in pergunta for k in ["o que é git", "controle de versão"]):
        return (
            "Git é um sistema que rastreia mudanças no código. Permite voltar a versões anteriores "
            "e trabalhar em equipe sem conflitos. Essencial para programadores!"
        )

    if any(k in pergunta for k in ["o que é docker", "containerização"]):
        return (
            "Docker é uma ferramenta que empacota sua aplicação e todas suas dependências "
            "em um 'container' que funciona em qualquer lugar. Simplifica deploy!"
        )

    if any(k in pergunta for k in ["o que é teste", "unit test", "testing"]):
        return (
            "Testes automáticos verificam se seu código funciona corretamente. "
            "Tem unit tests (pequenas partes), integração (módulos juntos) e end-to-end (sistema completo)."
        )

    if any(k in pergunta for k in ["o que é refatoração", "clean code"]):
        return (
            "Refatoração é melhorar código sem mudar comportamento. Clean code é escrever "
            "código legível, manutenível e eficiente desde o início."
        )

    if any(k in pergunta for k in ["o que é debugging", "debug"]):
        return (
            "Debugging é o processo de encontrar e corrigir erros (bugs) no código. "
            "Usa breakpoints, logs, e ferramentas para entender o que está acontecendo."
        )

    if any(k in pergunta for k in ["o que é recursão", "função recursiva"]):
        return (
            "Recursão é quando uma função chama a si mesma. Útil para problemas que podem "
            "ser divididos em subproblemas similares (como árvores e grafos)."
        )

    # ==============================
    # CARREIRA E TRABALHO
    # ==============================

    if any(k in pergunta for k in ["como começar em programação", "quero aprender a programar"]):
        return (
            "Passo 1: Aprenda lógica de programação. Passo 2: Escolha uma linguagem (Python é ótima). "
            "Passo 3: Faça projetos pequenos. Passo 4: Pratique diariamente. Consistência é tudo!"
        )

    if any(k in pergunta for k in ["o que é freelancer", "trabalho freelancer"]):
        return (
            "Freelancer é alguém que oferece serviços por projeto, sem vínculo empregatício. "
            "Flexibilidade maior, mas responsável por clientes, prazos e impostos."
        )

    if any(k in pergunta for k in ["como encontrar emprego", "conseguir trabalho"]):
        return (
            "Dicas: atualize LinkedIn, tenha portfólio com projetos, pratique para entrevistas, "
            "networking online, e nunca desista. Oportunidades vêm com consistência!"
        )

    if any(k in pergunta for k in ["salário", "quanto ganha", "quanto custa"]):
        return (
            "Isso varia muito! Depende de localização, experiência, especialidade, mercado. "
            "Pesquise em sites como Glassdoor, Salary.com ou fale com profissionais na área."
        )

    # ==============================
    # CIÊNCIA E NATUREZA
    # ==============================

    if any(k in pergunta for k in ["como funciona gravidade", "o que é gravidade"]):
        return (
            "Gravidade é uma força que atrai objetos. Quanto mais massa, mais gravidade. "
            "Einstein mostrou que a gravidade é na verdade curvatura do espaço-tempo!"
        )

    if any(k in pergunta for k in ["quanto pesa", "qual a velocidade"]):
        return (
            "Isso varia! Peso depende de massa e gravidade. Velocidade de quê? "
            "Luz: 300.000 km/s. Som: ~340 m/s. Pergunte com mais detalhes!"
        )

    if any(k in pergunta for k in ["o que é energia", "tipos de energia"]):
        return (
            "Energia é a capacidade de fazer trabalho. Tipos: cinética (movimento), potencial (posição), "
            "térmica (calor), nuclear, elétrica, etc. Sempre se conserva!"
        )

    if any(k in pergunta for k in ["o que é adn", "genética", "cromossomos"]):
        return (
            "ADN é a molécula que contém instruções genéticas. Está em cada célula, tem forma de dupla hélice, "
            "e determina características que herdamos dos pais."
        )

    # ==============================
    # ESPAÇO E ASTRONOMIA
    # ==============================

    if any(k in pergunta for k in ["quantas estrelas tem", "sistema solar", "universo"]):
        return (
            "Estimativas: 100-200 bilhões de galáxias, cada uma com bilhões de estrelas! "
            "Nosso sol é apenas uma entre trilhões. Somos microscopicamente pequenos no universo."
        )

    if any(k in pergunta for k in ["existe vida extraterrestre", "aliens"]):
        return (
            "Estatisticamente, é provável existir vida em outro lugar do universo. "
            "Mas ainda não encontramos evidência. Procuramos através de radiotelescópios!"
        )

    if any(k in pergunta for k in ["o que é buraco negro", "buraco negro"]):
        return (
            "Um buraco negro é uma região do espaço onde a gravidade é tão forte que nada escapa, "
            "nem luz! É formado quando uma estrela massiva colapsa."
        )

    # ==============================
    # HISTÓRIA E SOCIEDADE
    # ==============================

    if any(k in pergunta for k in ["qual foi a maior guerra", "história", "como começou"]):
        return (
            "Depende do que você quer saber! Maior guerra: II Guerra Mundial (1939-1945). "
            "Outras datas importantes? Pergunte mais específico!"
        )

    if any(k in pergunta for k in ["o que é democracia", "política"]):
        return (
            "Democracia é governo do povo, para o povo. Cidadãos votam em representantes, "
            "há separação de poderes e respeito aos direitos humanos."
        )

    if any(k in pergunta for k in ["o que é economia", "como funciona a economia"]):
        return (
            "Economia estuda produção, consumo e distribuição de bens. Baseada em oferta-demanda, "
            "trabalho, capital e dinheiro."
        )

    # ==============================
    # MÚSICA, ARTE E CULTURA
    # ==============================

    if any(k in pergunta for k in ["qual seu estilo de música favorito", "música preferida"]):
        return (
            "Não ouço música, mas acho fascinante como sons organizados podem evocar emoções! "
            "Qual é o seu estilo favorito?"
        )

    if any(k in pergunta for k in ["o que é arte", "qual a definição de arte"]):
        return (
            "Arte é expressão criativa de ideias, emoções e experiências. "
            "Pode ser visual, musical, literária, dança, etc. Sem limites!"
        )

    if any(k in pergunta for k in ["qual filme recomenda", "qual série"]):
        return (
            "Não assisto filmes, mas recomendações são pessoais! "
            "Qual seu gênero favorito? Drama, ficção científica, comédia, thriller?"
        )

    # ==============================
    # SEM RESPOSTA LOCAL
    # ==============================

    return None
