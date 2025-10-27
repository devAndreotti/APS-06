// ============================================================================
// VARIÁVEIS GLOBAIS
// ============================================================================

let startTime = Date.now();

// ============================================================================
// UTILITÁRIOS
// ============================================================================

/**
 * Atualiza elemento HTML por ID
 * @param {string} id - ID do elemento
 * @param {string|number} value - Valor a ser definido
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

const initUpload = () => {
  // Habilita o botão de upload se existir
  const uploadBtn = document.getElementById('uploadBtn');
  if (uploadBtn) {
    uploadBtn.disabled = false;
  }
};

// ============================================================================
// DADOS EM TEMPO REAL
// ============================================================================

/**
 * Busca dados em tempo real do backend via API
 */
const fetchData = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    
    // Atualizar dados principais
    updateElement('totalJumps', data.jumps);
    updateElement('currentStage', data.stage);
    updateElement('fps', data.fps);
    
    updateConnectionStatus(true);
    
  } catch (error) {
    console.error('Erro ao buscar dados:', error);
    updateConnectionStatus(false);
  }
};

/**
 * Atualiza status de conexão na interface
 * @param {boolean} connected - Status de conexão
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
 * Atualiza timer da sessão (webcam)
 */
const updateTimer = () => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  updateElement('timer', `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
};

/**
 * Atualiza duração do vídeo (upload)
 */
const updateDuration = () => {
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  const minutes = Math.floor(elapsed / 60);
  const seconds = elapsed % 60;
  updateElement('videoDuration', `${minutes}:${seconds.toString().padStart(2, '0')}`);
};

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

/**
 * Inicializa página de contador (webcam)
 */
const initContador = () => {
  // Resetar dados no backend
  fetch('/reset', { method: 'POST' }).catch(() => {});
  
  // Inicializar elementos com valores zerados
  updateElement('totalJumps', 0);
  updateElement('currentStage', 'Preparando');
  updateElement('fps', 0);
  
  setInterval(fetchData, 500);      // Buscar dados a cada 500ms
  setInterval(updateTimer, 1000);   // Atualizar timer a cada segundo
  fetchData();                      // Inicializar dados
  updateTimer();                    // Inicializar timer
};

/**
 * Inicializa página de upload de vídeo
 */
const initContadorVideo = () => {
  // Resetar dados no backend
  fetch('/reset', { method: 'POST' }).catch(() => {});
  
  // Inicializar elementos com valores zerados
  updateElement('totalJumps', 0);
  updateElement('currentStage', 'Preparando');
  updateElement('fps', 0);
  updateElement('videoDuration', '0:00');
  
  initUpload();                       // Inicializar sistema de upload
  setInterval(fetchData, 500);        // Buscar dados a cada 500ms
  setInterval(updateDuration, 1000);  // Atualizar duração a cada segundo
  fetchData();                        // Inicializar dados
  updateDuration();                   // Inicializar duração
};

/**
 * Inicializa página principal
 */
const initIndex = () => {
  initUpload(); // Apenas inicializar upload
};

// ============================================================================
// ROTEAMENTO E INICIALIZAÇÃO GLOBAL
// ============================================================================

/**
 * Detecta página atual e inicializa funções específicas
 */
const initPage = () => {
  const currentPage = window.location.pathname;
  
  if (currentPage === '/contador') {
    initContador();
  } else if (currentPage === '/contador_video') {
    // Verificar se há um vídeo sendo processado pela URL ou pelo HTML
    const hasVideoInUrl = window.location.search.includes('video=');
    const hasVideoInHtml = document.querySelector('.processing-section');
    
    if (hasVideoInUrl || hasVideoInHtml) {
      // Se há vídeo sendo processado, inicializar sistema de dados
      initContadorVideo();
    } else {
      // Se não há vídeo, apenas inicializar upload
      initUpload();
    }
  } else {
    initIndex();
  }
};

// Inicializar quando DOM estiver pronto
document.addEventListener('DOMContentLoaded', initPage);

// ============================================================================
// EXPOSIÇÃO GLOBAL
// ============================================================================
// Expor funções que são chamadas diretamente do HTML