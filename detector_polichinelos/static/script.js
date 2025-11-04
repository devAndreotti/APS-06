// ============================================================================
// VARIÁVEIS GLOBAIS
// ============================================================================

/**
 * Timestamp de quando a sessão foi iniciada (usado para calcular tempo decorrido)
 * @type {number}
 */
let startTime = Date.now();

/**
 * Contador de polichinelos anterior - usado para detectar incrementos
 * e acionar o efeito visual de destaque quando um novo polichinelo é detectado
 * @type {number}
 */
let previousJumps = 0;

// ============================================================================
// UTILITÁRIOS
// ============================================================================

/**
 * Atualiza o conteúdo de texto de um elemento HTML identificado por ID
 * @param {string} id - ID do elemento HTML a ser atualizado
 * @param {string|number} value - Novo valor a ser exibido no elemento
 * @returns {void}
 */
const updateElement = (id, value) => {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
};

// ============================================================================
// UPLOAD DE VÍDEO
// ============================================================================

/**
 * Inicializa o sistema de upload de vídeo, habilitando o botão de upload
 * quando o DOM estiver pronto
 * @returns {void}
 */
const initUpload = () => {
  const uploadBtn = document.getElementById('uploadBtn');
  if (uploadBtn) {
    uploadBtn.disabled = false;
  }
};

// ============================================================================
// DADOS EM TEMPO REAL
// ============================================================================

/**
 * Busca dados em tempo real do backend via API REST e atualiza a interface
 * - Atualiza contador de polichinelos, estágio atual e FPS
 * - Aciona efeito visual quando detecta novo polichinelo
 * - Atualiza status de conexão (conectado/desconectado)
 * @returns {Promise<void>}
 */
const fetchData = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    
    // Atualizar dados principais na interface
    updateElement('totalJumps', data.jumps);
    updateElement('currentStage', data.stage);
    updateElement('fps', data.fps);
    
    // Acionar efeito visual quando detecta incremento no contador
    if (typeof data.jumps === 'number' && data.jumps > previousJumps) {
      const primaryCard = getPrimaryHighlightElement();
      if (primaryCard) {
        applyJumpHighlight(primaryCard);
      }
    }
    
    // Atualizar contador anterior para próxima comparação
    if (typeof data.jumps === 'number') {
      previousJumps = data.jumps;
    }
    
    // Indicar que a conexão está ativa
    updateConnectionStatus(true);
    
  } catch (error) {
    console.error('Erro ao buscar dados:', error);
    // Indicar que a conexão falhou
    updateConnectionStatus(false);
  }
};

/**
 * Atualiza o indicador visual de status de conexão na interface
 * Modifica o ponto de status (verde/vermelho) e o texto (Conectado/Desconectado)
 * @param {boolean} connected - true se conectado ao backend, false caso contrário
 * @returns {void}
 */
const updateConnectionStatus = (connected) => {
  const statusDot = document.getElementById('statusDot');
  const statusText = document.getElementById('statusText');
  
  if (statusDot && statusText) {
    statusDot.className = connected ? 'status-dot active' : 'status-dot error';
    statusText.textContent = connected ? 'Conectado' : 'Desconectado';
  }
};

// ============================================================================
// TIMERS
// ============================================================================

/**
 * Atualiza o timer da sessão de detecção em tempo real (webcam)
 * Calcula o tempo decorrido desde o início da sessão e formata como MM:SS
 * @returns {void}
 */
const updateTimer = () => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  // Formata minutos e segundos com zero à esquerda (ex: 05:03)
  updateElement('timer', `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
};

/**
 * Atualiza a duração do vídeo sendo processado (upload)
 * Calcula o tempo decorrido desde o início do processamento e formata como M:SS
 * @returns {void}
 */
const updateDuration = () => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  // Formata minutos e segundos (ex: 5:03)
  updateElement('videoDuration', `${minutes}:${seconds.toString().padStart(2, '0')}`);
};

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

/**
 * Inicializa a página de contador para detecção em tempo real (webcam)
 * Configura valores iniciais, reseta o backend, prepara efeitos visuais
 * e inicia os intervalos de atualização de dados e timer
 * @returns {void}
 */
const initContador = () => {
  // Resetar dados no backend para começar nova sessão
  fetch('/reset', { method: 'POST' }).catch(() => {});
  
  // Inicializar elementos da interface com valores padrão
  updateElement('totalJumps', 0);
  updateElement('currentStage', 'Preparando');
  updateElement('fps', 0);
  previousJumps = 0;
  
  // Preparar efeito visual no primeiro card
  preparePrimaryHighlight();
  
  // Configurar atualizações periódicas
  setInterval(fetchData, 500);      // Buscar dados do backend a cada 500ms
  setInterval(updateTimer, 1000);   // Atualizar timer a cada segundo
  
  // Atualizar dados e timer imediatamente
  fetchData();
  updateTimer();
};

/**
 * Inicializa a página de processamento de vídeo enviado
 * Configura valores iniciais, reseta o backend, prepara efeitos visuais
 * e inicia os intervalos de atualização de dados e duração do vídeo
 * @returns {void}
 */
const initContadorVideo = () => {
  // Resetar dados no backend para começar novo processamento
  fetch('/reset', { method: 'POST' }).catch(() => {});
  
  // Inicializar elementos da interface com valores padrão
  updateElement('totalJumps', 0);
  updateElement('currentStage', 'Preparando');
  updateElement('fps', 0);
  updateElement('videoDuration', '0:00');
  previousJumps = 0;
  
  // Preparar efeito visual no primeiro card
  preparePrimaryHighlight();
  
  // Inicializar sistema de upload de vídeo
  initUpload();
  
  // Configurar atualizações periódicas
  setInterval(fetchData, 500);        // Buscar dados do backend a cada 500ms
  setInterval(updateDuration, 1000);  // Atualizar duração do vídeo a cada segundo
  
  // Atualizar dados e duração imediatamente
  fetchData();
  updateDuration();
};

/**
 * Inicializa a página principal (index)
 * Apenas habilita o sistema de upload de vídeo
 * @returns {void}
 */
const initIndex = () => {
  initUpload();
};

// ============================================================================
// ROTEAMENTO E INICIALIZAÇÃO GLOBAL
// ============================================================================

/**
 * Detecta a página atual através da URL e inicializa as funções específicas
 * para cada página (contador webcam, upload de vídeo ou página principal)
 * @returns {void}
 */
const initPage = () => {
  const currentPage = window.location.pathname;
  
  if (currentPage === '/contador') {
    // Página de detecção em tempo real via webcam
    initContador();
  } else if (currentPage === '/contador_video') {
    // Página de processamento de vídeo enviado
    // Verificar se há um vídeo sendo processado pela URL ou pelo HTML
    const hasVideoInUrl = window.location.search.includes('video=');
    const hasVideoInHtml = document.querySelector('.processing-section');
    
    if (hasVideoInUrl || hasVideoInHtml) {
      // Se há vídeo sendo processado, inicializar sistema completo de dados
      initContadorVideo();
    } else {
      // Se não há vídeo, apenas inicializar sistema de upload
      initUpload();
    }
  } else {
    // Página principal (index) - apenas inicializar upload
    initIndex();
  }
};

// Aguardar o DOM estar completamente carregado antes de inicializar
document.addEventListener('DOMContentLoaded', initPage);

// ============================================================================
// EXPOSIÇÃO GLOBAL
// ============================================================================
// Expor funções que são chamadas diretamente do HTML ou por outros scripts

// ============================================================================
// REALCE DINÂMICO NO PRIMEIRO CARD
// ============================================================================

/**
 * Retorna o primeiro card da página que deve receber o efeito visual de destaque
 * Procura primeiro em .data-grid, depois em .stats-grid (dependendo da página)
 * @returns {HTMLElement|null} O elemento do primeiro card ou null se não encontrado
 */
const getPrimaryHighlightElement = () => {
  // Tentar encontrar o primeiro item no grid de dados
  const firstDataItem = document.querySelector('.data-grid .data-item');
  if (firstDataItem) return firstDataItem;
  
  // Se não encontrar, tentar no grid de estatísticas
  const firstStatItem = document.querySelector('.stats-grid .stat-item');
  if (firstStatItem) return firstStatItem;
  
  return null;
};

/**
 * Gera valores HSL (matiz, saturação, luminosidade) para uma cor suave e moderna
 * A matiz é aleatória (0-360°), saturação e luminosidade são fixas para consistência visual
 * @returns {{hue: number, saturation: number, lightness: number}} Objeto com valores HSL
 */
const generateSoftHsl = () => {
  const hue = Math.floor(Math.random() * 360); // Matiz aleatória (toda a roda de cores)
  const saturation = 70; // Saturação fixa em 70% (cores vibrantes mas não exageradas)
  const lightness = 60;  // Luminosidade fixa em 60% (nem muito claro nem muito escuro)
  return { hue, saturation, lightness };
};

/**
 * Prepara um elemento HTML para receber o efeito de destaque visual
 * Adiciona transições CSS suaves e garante que o elemento tenha uma borda visível
 * @param {HTMLElement} el - Elemento HTML a ser preparado
 * @returns {void}
 */
const prepareElementHighlight = (el) => {
  if (!el) return;
  
  const current = getComputedStyle(el);
  
  // Adicionar transições suaves para background, border e box-shadow
  // Preserva transições existentes e adiciona novas
  el.style.transition = `${current.transition ? current.transition + ', ' : ''}background 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease`;
  
  // Garantir que o elemento tenha uma borda visível (necessária para o efeito)
  if (!current.borderColor || current.borderColor === 'rgba(0, 0, 0, 0)') {
    el.style.border = '1px solid var(--color-border)';
  }
};

/**
 * Prepara o primeiro card da página para receber o efeito de destaque
 * Esta função é chamada na inicialização da página
 * @returns {void}
 */
const preparePrimaryHighlight = () => {
  const el = getPrimaryHighlightElement();
  if (!el) return;
  prepareElementHighlight(el);
};

/**
 * Aplica o efeito visual de destaque quando um novo polichinelo é detectado
 * Gera uma cor aleatória suave e aplica gradiente, borda colorida e sombra com brilho
 * @param {HTMLElement} element - Elemento HTML (card) que receberá o efeito
 * @returns {void}
 */
const applyJumpHighlight = (element) => {
  // Gerar valores HSL para uma cor suave e moderna
  const { hue, saturation, lightness } = generateSoftHsl();
  
  // Criar variações da cor com diferentes opacidades
  const baseHsl = `hsl(${hue} ${saturation}% ${lightness}%)`;              // Cor sólida para borda
  const glowHsla = `hsla(${hue} ${saturation}% ${lightness}% / 0.35)`;     // Cor com transparência para sombra (35%)
  const gradTop = `hsla(${hue} ${saturation}% ${lightness}% / 0.28)`;      // Cor com transparência para gradiente (28%)

  // Aplicar estilos visuais ao elemento
  // Gradiente de cima para baixo com a cor suave, depois fundo padrão do card
  element.style.background = `linear-gradient(0deg, ${gradTop}, hsla(0 0% 0% / 0)), var(--color-bg-card)`;
  // Borda colorida com a cor sólida
  element.style.borderColor = baseHsl;
  // Sombra com brilho colorido para efeito de profundidade
  element.style.boxShadow = `0 6px 18px ${glowHsla}`;
};

// Disponibilizar funções globalmente para uso em outros scripts (ex: contador_multi.html)
window.applyJumpHighlight = applyJumpHighlight;
window.preparePrimaryHighlight = preparePrimaryHighlight;
window.getPrimaryHighlightElement = getPrimaryHighlightElement;
window.prepareElementHighlight = prepareElementHighlight;