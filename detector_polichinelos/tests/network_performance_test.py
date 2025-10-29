#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Performance e Uso de Recursos do Sistema
=================================================

Este script realiza uma análise completa de desempenho da aplicação web local,
coletando métricas de CPU, memória, rede e tempo de carregamento das páginas.

Funcionalidades:
- Navegação automática entre páginas da aplicação
- Coleta de métricas de sistema em tempo real
- Geração de relatórios em JSON, HTML e PNG
- Análise de tráfego de rede e performance de carregamento
"""

# =============================================================================
# IMPORTAÇÕES E CONFIGURAÇÕES INICIAIS
# =============================================================================

import sys
import os

# Configuração de encoding para Windows (correção de caracteres especiais)
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Bibliotecas padrão do Python
import asyncio
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any

# Bibliotecas de terceiros para monitoramento e análise
import psutil  # Monitoramento de sistema (CPU, memória)
import matplotlib.pyplot as plt  # Geração de gráficos
import matplotlib.dates as mdates  # Formatação de datas nos gráficos
from playwright.async_api import async_playwright, Page, Browser  # Automação de navegador
from dataclasses import dataclass, asdict  # Estruturas de dados tipadas


# =============================================================================
# CLASSE DE CORES E FORMATAÇÃO PARA TERMINAL
# =============================================================================

class Colors:
    """
    Classe para formatação e cores no terminal.
    
    Fornece métodos para aplicar cores ANSI, emojis com fallback para Windows,
    e formatação de tabelas e cards no terminal.
    """
    # Códigos de cores ANSI
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    # Detectar se o terminal suporta emojis
    @staticmethod
    def supports_emoji():
        """Detecta se o terminal suporta emojis"""
        try:
            import sys
            import os
            # Windows PowerShell/CMD geralmente não suporta emojis
            if os.name == 'nt':
                return False
            # Linux/Mac geralmente suportam
            return True
        except:
            return False
    
    # Emojis com fallback para Windows
    @staticmethod
    def get_emoji(emoji_char, fallback_text):
        """Retorna emoji se suportado, senão texto alternativo"""
        if Colors.supports_emoji():
            return emoji_char
        return fallback_text
    
    ROCKET = '🚀'
    CLOCK = '⏱️'
    BRAIN = '🧠'
    GLOBE = '🌐'
    TROPHY = '🏆'
    MAGNIFYING = '🔍'
    WARNING = '⚠️'
    CHECK = '✅'
    INFO = 'ℹ️'
    CHART = '📊'
    FOLDER = '📁'
    SUCCESS = '🎉'
    QUESTION = '❓'
    ERROR = '❌'
    LOADING = '⏳'
    LIST = '📋'
    
    @staticmethod
    def colored(text: str, color: str) -> str:
        """Aplica cor ao texto"""
        return f"{color}{text}{Colors.END}"
    
    @staticmethod
    def success(text: str) -> str:
        """Texto de sucesso em verde"""
        return Colors.colored(text, Colors.GREEN)
    
    @staticmethod
    def error(text: str) -> str:
        """Texto de erro em vermelho"""
        return Colors.colored(text, Colors.RED)
    
    @staticmethod
    def warning(text: str) -> str:
        """Texto de aviso em amarelo"""
        return Colors.colored(text, Colors.YELLOW)
    
    @staticmethod
    def info(text: str) -> str:
        """Texto informativo em azul"""
        return Colors.colored(text, Colors.BLUE)
    
    @staticmethod
    def highlight(text: str) -> str:
        """Texto destacado em ciano"""
        return Colors.colored(text, Colors.CYAN)
    
    @staticmethod
    def bold(text: str) -> str:
        """Texto em negrito"""
        return Colors.colored(text, Colors.BOLD)
    
    @staticmethod
    def cyan(text: str) -> str:
        """Texto em ciano"""
        return Colors.colored(text, Colors.CYAN)
    
    @staticmethod
    def green(text: str) -> str:
        """Texto em verde"""
        return Colors.colored(text, Colors.GREEN)
    
    @staticmethod
    def yellow(text: str) -> str:
        """Texto em amarelo"""
        return Colors.colored(text, Colors.YELLOW)
    
    @staticmethod
    def blue(text: str) -> str:
        """Texto em azul"""
        return Colors.colored(text, Colors.BLUE)
    
    @staticmethod
    def red(text: str) -> str:
        """Texto em vermelho"""
        return Colors.colored(text, Colors.RED)
    
    @staticmethod
    def magenta(text: str) -> str:
        """Texto em magenta"""
        return Colors.colored(text, Colors.MAGENTA)
    
    @staticmethod
    def print_header(title: str, width: int = 80):
        """Imprime cabeçalho formatado"""
        print("\n" + "=" * width, flush=True)
        print(f" {title} ", flush=True)
        print("=" * width, flush=True)
    
    @staticmethod
    def print_section(title: str, width: int = 80):
        """Imprime seção formatada"""
        print("\n" + "─" * width, flush=True)
        print(f" {title} ", flush=True)
        print("─" * width + "\n", flush=True)
    
    @staticmethod
    def print_subsection(title: str, width: int = 80):
        """Imprime subseção formatada"""
        print("\n" + "─" * width)
        print(f" {title} ")
        print("─" * width + "\n")
    
    @staticmethod
    def print_card(title: str, value: str, icon: str = "", color: str = None):
        """Imprime um card formatado"""
        if color is None:
            color = Colors.CYAN
        if icon:
            print(f"  {icon} {Colors.bold(Colors.colored(title, color))}: {Colors.bold(value)}")
        else:
            print(f"  {Colors.bold(Colors.colored(title, color))}: {Colors.bold(value)}")
    
    @staticmethod
    def print_table_header(headers: list, widths: list):
        """Imprime cabeçalho de tabela"""
        header_line = ""
        separator_line = ""
        for i, (header, width) in enumerate(zip(headers, widths)):
            header_line += f"{Colors.bold(Colors.info(header)):<{width}}"
            separator_line += "─" * width
            if i < len(headers) - 1:
                header_line += " │ "
                separator_line += "─"
        
        print(f"┌{separator_line}┐")
        print(f"│ {header_line} │")
        print(f"├{separator_line}┤")
    
    @staticmethod
    def print_table_row(values: list, widths: list, colors: list = None):
        """Imprime linha de tabela"""
        if colors is None:
            colors = [Colors.WHITE] * len(values)
        
        row_line = ""
        for i, (value, width, color) in enumerate(zip(values, widths, colors)):
            formatted_value = f"{Colors.colored(str(value), color):<{width}}"
            row_line += formatted_value
            if i < len(values) - 1:
                row_line += " │ "
        
        print(f"│ {row_line} │")
    
    @staticmethod
    def print_table_footer(widths: list):
        """Imprime rodapé de tabela"""
        separator_line = "─" * sum(widths) + "─" * (len(widths) - 1)
        print(f"└{separator_line}┘")


# =============================================================================
# FUNÇÕES DE VERIFICAÇÃO E VALIDAÇÃO
# =============================================================================

def check_dependencies():
    """
    Verifica se todas as dependências necessárias estão instaladas.
    
    Returns:
        bool: True se todas as dependências estão disponíveis, False caso contrário
    """
    print(f"{Colors.info('Verificando dependências...')}")
    
    dependencies_ok = True
    
    try:
        import playwright
        print(f"  ✅ {Colors.success('Playwright instalado')}")
    except ImportError:
        print(f"  ❌ {Colors.error('Playwright não instalado')}")
        dependencies_ok = False
    
    try:
        import psutil
        print(f"  ✅ {Colors.success('psutil instalado')}")
    except ImportError:
        print(f"  ❌ {Colors.error('psutil não instalado')}")
        dependencies_ok = False
    
    try:
        import matplotlib
        print(f"  ✅ {Colors.success('matplotlib instalado')}")
    except ImportError:
        print(f"  ❌ {Colors.error('matplotlib não instalado')}")
        dependencies_ok = False
    
    if dependencies_ok:
        print(f"\n{Colors.success('Todas as dependências estão instaladas!')}")
    else:
        print(f"\n{Colors.error('Algumas dependências estão faltando')}")
        print(f"{Colors.info('Execute: pip install playwright psutil matplotlib')}")
    
    return dependencies_ok


def check_playwright_browsers():
    """
    Verifica se os navegadores do Playwright estão instalados.
    
    Nota: Verificação simplificada pois o teste falharia automaticamente
    se os navegadores não estivessem disponíveis.
    
    Returns:
        bool: Sempre retorna True (verificação implícita durante execução)
    """
    # Verificação removida - não é necessária pois o teste falharia se não funcionasse
    return True


def check_flask_app():
    """
    Verifica se a aplicação Flask está rodando e acessível.
    
    Faz uma requisição HTTP para localhost:5000 para confirmar
    que o servidor está ativo e respondendo.
    
    Returns:
        bool: True se Flask está rodando, False caso contrário
    """
    print(f"\n{Colors.info('Verificando se a aplicação Flask está rodando...')}")
    
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print(f"  ✅ {Colors.success('Aplicação Flask está rodando!')}")
            return True
        else:
            print(f"  ❌ {Colors.error(f'Aplicação Flask retornou status: {response.status_code}')}")
            return False
    except requests.exceptions.RequestException:
        print(f"  ❌ {Colors.error('Aplicação Flask não está rodando')}")
        print(f"  {Colors.info('Execute: python app.py')}")
        return False


def ask_user_confirmation():
    """
    Solicita confirmação do usuário antes de iniciar o teste.
    
    Informa sobre o que será executado e pede confirmação.
    Em ambientes não interativos (CI/CD), continua automaticamente.
    
    Returns:
        bool: True se usuário confirma ou em ambiente não interativo, False caso contrário
    """
    print(f"\n{Colors.warning('ATENÇÃO:')}")
    print(f"  • O teste abrirá um navegador em tela cheia")
    print(f"  • Não feche o navegador durante a execução")
    print(f"  • O processo pode levar alguns minutos")
    print(f"  • O relatório HTML será aberto automaticamente ao final")
    
    try:
        while True:
            response = input(f"\n{Colors.bold(Colors.info('Deseja continuar? (S/n): '))}").strip().lower()
            if response in ['s', 'sim', 'y', 'yes', '']:
                return True
            elif response in ['n', 'nao', 'no']:
                return False
            else:
                print(f"  {Colors.warning('Resposta inválida. Digite S para sim ou N para não.')}")
    except (EOFError, KeyboardInterrupt):
        # Se não há input disponível (ambiente não interativo), continuar automaticamente
        print(f"\n{Colors.info('Continuando automaticamente...')}")
        return True


# =============================================================================
# CLASSES DE DADOS PARA MÉTRICAS
# =============================================================================

@dataclass
class PageMetrics:
    """
    Estrutura de dados para armazenar métricas de uma página específica.
    
    Contém informações sobre tempo de carregamento, uso de recursos,
    tráfego de rede e requisições HTTP para uma única página.
    """
    name: str
    load_time: float
    dom_load_time: float
    total_data_downloaded: float  # em KB
    http_requests_count: int
    avg_memory_mb: float  # Memória do processo Python (teste)
    avg_cpu_percent: float
    max_memory_mb: float  # Memória do processo Python (teste)
    min_memory_mb: float  # Memória do processo Python (teste)
    avg_flask_memory_mb: float = 0.0  # Memória média do processo Flask
    max_flask_memory_mb: float = 0.0  # Memória máxima do processo Flask
    browser_memory_mb: float = 0.0  # Memória do navegador (JavaScript heap)
    avg_fps: float = 0.0  # Média de FPS (apenas para contador_video)


@dataclass
class SystemMetrics:
    """
    Estrutura de dados para métricas do sistema em um momento específico.
    
    Armazena informações sobre uso de CPU, memória e rede
    coletadas durante o monitoramento contínuo do sistema.
    """
    timestamp: float
    memory_mb: float  # Memória do processo Python (teste)
    cpu_percent: float
    network_data_kb: float
    flask_memory_mb: float = 0.0  # Memória do processo Flask (se encontrado)
    browser_memory_mb: float = 0.0  # Memória do navegador (JavaScript heap)


# =============================================================================
# CLASSE PRINCIPAL DE MONITORAMENTO DE PERFORMANCE
# =============================================================================

class PerformanceMonitor:
    """
    Monitor principal de performance do sistema.
    
    Coordena a execução dos testes, coleta de métricas e geração de relatórios.
    Utiliza Playwright para automação de navegador e psutil para monitoramento de sistema.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.pages_to_test = [
            "/",  # Página inicial (rota raiz)
            "/contador", 
            "/contador_multi",
            "/contador_video"  # Corrigido: sem capitalização
        ]
        
        # Dados coletados
        self.page_metrics: List[PageMetrics] = []
        self.system_metrics: List[SystemMetrics] = []
        self.start_time = None
        self.end_time = None
        
        # Controle de monitoramento
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Configuração de diretórios
        self.reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Cache do processo Flask encontrado (evita buscar toda vez)
        self.flask_process = None
    
    def find_flask_process(self):
        """
        Encontra o processo Flask rodando no sistema.
        
        Procura por processos Python que estejam executando app.py
        ou Flask. Cria um cache para não buscar repetidamente.
        
        Returns:
            psutil.Process ou None: Processo Flask encontrado ou None se não encontrar
        """
        # Se já encontramos o processo antes, verificar se ainda está ativo
        if self.flask_process:
            try:
                # Testar se o processo ainda existe
                self.flask_process.status()
                return self.flask_process
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Processo não existe mais, limpar cache
                self.flask_process = None
        
        # Procurar por processos Flask
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline')
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        # Procurar por app.py ou flask
                        if ('app.py' in cmdline_str or 'flask' in cmdline_str) and 'python' in cmdline_str:
                            # Evitar pegar o próprio processo do teste
                            if 'network_performance_test' not in cmdline_str:
                                self.flask_process = proc
                                return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception:
            pass
        
        return None
    
    def start_system_monitoring(self):
        """
        Inicia o monitoramento contínuo do sistema em thread separada.
        
        Coleta métricas de CPU e memória a cada 0.5 segundos
        enquanto o teste está em execução.
        Agora também monitora o processo Flask separadamente.
        """
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    # Obter métricas do processo Python atual (teste)
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024  # Converter para MB
                    
                    # Tentar encontrar e monitorar processo Flask
                    flask_memory_mb = 0.0
                    flask_proc = self.find_flask_process()
                    if flask_proc:
                        try:
                            flask_memory_info = flask_proc.memory_info()
                            flask_memory_mb = flask_memory_info.rss / 1024 / 1024  # Converter para MB
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # Processo Flask não acessível, limpar cache
                            self.flask_process = None
                    
                    # Obter uso de CPU
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    
                    # Criar métrica do sistema
                    metric = SystemMetrics(
                        timestamp=time.time(),
                        memory_mb=memory_mb,
                        cpu_percent=cpu_percent,
                        network_data_kb=0,  # Será atualizado durante navegação
                        flask_memory_mb=flask_memory_mb,
                        browser_memory_mb=0.0  # Será preenchido durante coleta de página
                    )
                    
                    self.system_metrics.append(metric)
                    
                    # Aguardar antes da próxima medição
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Erro no monitoramento: {e}")
                    break
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_system_monitoring(self):
        """
        Para o monitoramento contínuo do sistema.
        
        Sinaliza para a thread de monitoramento parar e aguarda
        sua finalização com timeout de 2 segundos.
        """
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
    
    async def collect_page_metrics(self, page: Page, page_name: str) -> PageMetrics:
        """
        Coleta métricas específicas de uma página web.
        
        Navega para a página, intercepta requisições HTTP, mede tempos
        de carregamento e coleta dados de uso de recursos.
        
        Args:
            page: Instância da página do Playwright
            page_name: Nome/rota da página a ser testada
            
        Returns:
            PageMetrics: Objeto contendo todas as métricas coletadas
        """
        # Variáveis para coleta de dados de rede
        total_data_downloaded = 0
        http_requests_count = 0
        tracked_responses = []  # Lista para rastrear respostas e medir depois
        
        # Interceptar respostas HTTP para medir tráfego
        async def handle_response(response):
            nonlocal total_data_downloaded, http_requests_count
            
            try:
                # Contar requisições
                http_requests_count += 1
                
                # Para streaming multipart, vamos armazenar a resposta para medir depois
                # pois streaming não tem content-length fixo e o body pode estar incompleto
                url = response.url
                if 'video_feed' in url or 'video_feed_multi' in url:
                    # Streaming de vídeo - vamos medir periodicamente
                    tracked_responses.append(response)
                else:
                    # Requisições normais - medir normalmente
                    content_length = response.headers.get('content-length')
                    if content_length:
                        total_data_downloaded += int(content_length)
                    else:
                        # Se não houver content-length, tentar obter o corpo da resposta
                        try:
                            body = await response.body()
                            total_data_downloaded += len(body)
                        except:
                            pass  # Ignorar erros ao obter o corpo
                        
            except Exception as e:
                # Não imprimir erro para não poluir a saída, apenas ignorar
                pass
        
        # Registrar handler de resposta
        page.on('response', handle_response)
        
        # Medir tempo de carregamento
        start_navigation = time.time()
        
        # Navegar para a página
        await page.goto(f"{self.base_url}{page_name}", wait_until='domcontentloaded')
        
        # Capturar tempo imediatamente após carregamento
        end_navigation = time.time()
        load_time = end_navigation - start_navigation
        
        # Aguardar um pouco para garantir que todas as requisições sejam capturadas
        await page.wait_for_timeout(1000)
        
        # Mostrar mensagem de carregamento para páginas especiais (antes de coletar FPS)
        if page_name == "/contador" or page_name == "/contador_multi":
            print(f"  ✅ {Colors.success(f'Página {page_name} carregada em {load_time:.2f}s')}", flush=True)
        
        # Se for a página contador_video, interagir com upload e processar vídeo
        avg_fps = 0.0
        if page_name == "/contador_video":
            try:
                # Mostrar mensagem de carregamento primeiro
                print(f"  ✅ {Colors.success(f'Página /contador_video carregada em {load_time:.2f}s')}", flush=True)
                print(f"  \n📹 {Colors.info('Interagindo com file input na página contador_video...')}", flush=True)
                # Aguardar o label aparecer
                await page.wait_for_selector('label[for="videoInput"]', timeout=5000)
                
                # Obter o caminho do primeiro vídeo MP4 na pasta uploads
                uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
                
                # Procurar o primeiro arquivo MP4
                mp4_files = []
                if os.path.exists(uploads_dir):
                    for file in os.listdir(uploads_dir):
                        if file.lower().endswith('.mp4'):
                            mp4_files.append(os.path.join(uploads_dir, file))
                
                if mp4_files:
                    # Ordenar para pegar o primeiro
                    mp4_files.sort()
                    first_mp4 = mp4_files[0]
                    
                    print(f"  📁 {Colors.info(f'Selecionando vídeo: {os.path.basename(first_mp4)}')}", flush=True)
                    
                    # Selecionar o arquivo diretamente no input
                    video_input = page.locator('#videoInput')
                    await video_input.set_input_files(first_mp4)
                    
                    print(f"  ✅ {Colors.success('Vídeo selecionado! Enviando formulário...')}", flush=True)
                    
                    # Clicar no botão "Processar Vídeo" para submeter o formulário
                    submit_button = page.locator('button[type="submit"]')
                    await submit_button.click()
                    
                    # Aguardar o redirecionamento para a página de processamento
                    print(f"  \n🔄 {Colors.info('Aguardando redirecionamento após upload...')}", flush=True)
                    await page.wait_for_url(
                        lambda url: 'contador_video' in url and 'video=' in url,
                        timeout=15000
                    )
                    
                    print(f"  ⏳ {Colors.info('Aguardando vídeo iniciar processamento...')}", flush=True)
                    
                    # Aguardar a seção de processamento aparecer
                    await page.wait_for_selector('.processing-section', timeout=10000)
                    await page.wait_for_selector('#fps', timeout=5000)
                    
                    # Aguardar o vídeo realmente começar (FPS > 0)
                    max_wait_start = 30  # Máximo 30 segundos esperando iniciar
                    waited_start = 0
                    fps_started = False
                    
                    while waited_start < max_wait_start and not fps_started:
                        await page.wait_for_timeout(1000)
                        waited_start += 1
                        
                        # Buscar FPS atual via API
                        try:
                            fps_value = await page.evaluate("""
                                async () => {
                                    try {
                                        const response = await fetch('/api/data');
                                        const data = await response.json();
                                        return parseFloat(data.fps) || 0;
                                    } catch (e) {
                                        return 0;
                                    }
                                }
                            """)
                            
                            if fps_value > 0:
                                fps_started = True
                                print(f"  🎬 {Colors.success(f'Vídeo iniciado! FPS inicial: {fps_value:.2f}')}", flush=True)
                                break
                        except:
                            pass
                        
                        if waited_start % 5 == 0:
                            print(f"  ⏳ {Colors.info(f'Aguardando vídeo iniciar... ({waited_start}s)')}", flush=True)
                    
                    if not fps_started:
                        print(f"  ⚠️ {Colors.warning('Vídeo não iniciou dentro do tempo esperado. Continuando...')}", flush=True)
                    else:
                        # Coletar métricas de FPS durante 10 segundos (a cada 500ms = 20 amostras)
                        print(f"  \n📊 {Colors.info('Coletando FPS durante 10 segundos (a cada 500ms)...')}", flush=True)
                        fps_samples = []
                        collection_duration = 20  # 20 amostras a cada 500ms = 10 segundos
                        
                        for i in range(collection_duration):
                            await page.wait_for_timeout(500)  # Aguardar 500ms entre amostras (mesma frequência da tela)
                            
                            # Buscar FPS atual da API
                            try:
                                fps_from_api = await page.evaluate("""
                                    async () => {
                                        try {
                                            const response = await fetch('/api/data');
                                            const data = await response.json();
                                            return parseFloat(data.fps) || 0;
                                        } catch (e) {
                                            return 0;
                                        }
                                    }
                                """)
                                
                                if fps_from_api > 0:
                                    fps_samples.append(fps_from_api)
                                    
                                    # Mostrar progresso a cada 2 segundos (4 amostras)
                                    if (i + 1) % 4 == 0:
                                        elapsed_seconds = (i + 1) * 0.5
                                        current_avg = sum(fps_samples) / len(fps_samples) if fps_samples else 0
                                        print(f"    📈 {Colors.info(f'[{elapsed_seconds:.1f}s/10s] FPS atual: {fps_from_api:.2f} | Média: {current_avg:.2f}')}", flush=True)
                                    
                            except Exception as e:
                                if i == 0:
                                    print(f"    ⚠️ {Colors.warning(f'Erro ao coletar FPS: {e}')}", flush=True)
                        
                        # Calcular média de FPS
                        if fps_samples:
                            avg_fps = sum(fps_samples) / len(fps_samples)
                            max_fps = max(fps_samples)
                            min_fps = min(fps_samples)
                            print(f"\n  📊 {Colors.success('Métricas de FPS coletadas (contador_video):')}", flush=True)
                            print(f"    • Amostras: {Colors.cyan(f'{len(fps_samples)} (coletadas a cada 500ms em 10s)')}", flush=True)
                            print(f"    • Média: {Colors.cyan(f'{avg_fps:.2f} FPS')}", flush=True)
                            print(f"    • Máximo: {Colors.green(f'{max_fps:.2f} FPS')}", flush=True)
                            print(f"    • Mínimo: {Colors.yellow(f'{min_fps:.2f} FPS')}", flush=True)
                        else:
                            print(f"  ⚠️ {Colors.warning('Nenhuma amostra de FPS válida coletada')}", flush=True)
                        
                        # Clicar em "Voltar" após coletar FPS
                        print(f"  🔙 {Colors.info('Clicando em Voltar...')}", flush=True)
                        try:
                            back_button = page.locator('a.btn-back, a[href="/"]')
                            await back_button.click()
                            await page.wait_for_timeout(1000)
                        except Exception as e:
                            print(f"  ⚠️ {Colors.warning(f'Erro ao clicar em Voltar: {e}')}", flush=True)
                else:
                    print(f"  ⚠️ {Colors.warning('Nenhum vídeo MP4 encontrado na pasta uploads')}", flush=True)
                    
            except Exception as e:
                print(f"  ⚠️ {Colors.warning(f'Erro ao interagir com vídeo: {e}')}", flush=True)
                import traceback
                traceback.print_exc()
                # Continuar mesmo se houver erro
        
        # Se for a página contador (webcam), coletar FPS por 10 segundos
        if page_name == "/contador":
            try:
                print(f"\n  📹 {Colors.info('Aguardando webcam iniciar...')}", flush=True)
                
                # Aguardar elementos aparecerem
                await page.wait_for_selector('#fps', timeout=10000)
                
                # Aguardar o vídeo realmente começar (FPS > 0)
                max_wait_start = 30
                waited_start = 0
                fps_started = False
                
                while waited_start < max_wait_start and not fps_started:
                    await page.wait_for_timeout(1000)
                    waited_start += 1
                    
                    try:
                        fps_value = await page.evaluate("""
                            async () => {
                                try {
                                    const response = await fetch('/api/data');
                                    const data = await response.json();
                                    return parseFloat(data.fps) || 0;
                                } catch (e) {
                                    return 0;
                                }
                            }
                        """)
                        
                        if fps_value > 0:
                            fps_started = True
                            print(f"  🎬 {Colors.success(f'Webcam iniciada! FPS inicial: {fps_value:.2f}')}", flush=True)
                            break
                    except:
                        pass
                    
                    if waited_start % 5 == 0:
                        print(f"  ⏳ {Colors.info(f'Aguardando webcam iniciar... ({waited_start}s)')}", flush=True)
                
                if fps_started:
                    # Coletar FPS por 10 segundos (a cada 500ms = 20 amostras)
                    print(f"\n  📊 {Colors.info('Coletando FPS (webcam) durante 10 segundos (a cada 500ms)...')}", flush=True)
                    fps_samples = []
                    
                    for i in range(20):  # 20 amostras a cada 500ms = 10 segundos
                        await page.wait_for_timeout(500)  # Aguardar 500ms entre amostras (mesma frequência da tela)
                        
                        try:
                            fps_from_api = await page.evaluate("""
                                async () => {
                                    try {
                                        const response = await fetch('/api/data');
                                        const data = await response.json();
                                        return parseFloat(data.fps) || 0;
                                    } catch (e) {
                                        return 0;
                                    }
                                }
                            """)
                            
                            if fps_from_api > 0:
                                fps_samples.append(fps_from_api)
                                # Mostrar progresso a cada 2 segundos (4 amostras)
                                if (i + 1) % 4 == 0:
                                    elapsed_seconds = (i + 1) * 0.5
                                    current_avg = sum(fps_samples) / len(fps_samples) if fps_samples else 0
                                    print(f"    📈 {Colors.info(f'[{elapsed_seconds:.1f}s/10s] FPS atual: {fps_from_api:.2f} | Média: {current_avg:.2f}')}", flush=True)
                        except:
                            pass
                    
                    if fps_samples:
                        avg_fps = sum(fps_samples) / len(fps_samples)
                        max_fps = max(fps_samples)
                        min_fps = min(fps_samples)
                        print(f"\n  📊 {Colors.success('Métricas de FPS coletadas (webcam):')}", flush=True)
                        print(f"    • Amostras: {Colors.cyan(f'{len(fps_samples)} (coletadas a cada 500ms em 10s)')}", flush=True)
                        print(f"    • Média: {Colors.cyan(f'{avg_fps:.2f} FPS')}", flush=True)
                        print(f"    • Máximo: {Colors.green(f'{max_fps:.2f} FPS')}", flush=True)
                        print(f"    • Mínimo: {Colors.yellow(f'{min_fps:.2f} FPS')}", flush=True)
                    
            except Exception as e:
                print(f"  ⚠️ {Colors.warning(f'Erro ao coletar FPS da webcam: {e}')}", flush=True)
        
        # Se for a página contador_multi (duas pessoas), coletar FPS por 10 segundos
        elif page_name == "/contador_multi":
            try:
                print(f"\n  👥 {Colors.info('Aguardando modo duas pessoas iniciar...')}", flush=True)
                
                # Aguardar container de dados aparecer (não existe #fps nesta página)
                await page.wait_for_selector('#pessoas-container', timeout=10000)
                
                # Aguardar o vídeo realmente começar (FPS > 0)
                max_wait_start = 30
                waited_start = 0
                fps_started = False
                
                while waited_start < max_wait_start and not fps_started:
                    await page.wait_for_timeout(1000)
                    waited_start += 1
                    
                    try:
                        # Para modo multi, buscar da API /api/data_multi
                        fps_value = await page.evaluate("""
                            async () => {
                                try {
                                    const response = await fetch('/api/data_multi');
                                    const data = await response.json();
                                    if (data.pessoas && data.pessoas.length > 0) {
                                        return parseFloat(data.pessoas[0].fps) || 0;
                                    }
                                    return 0;
                                } catch (e) {
                                    return 0;
                                }
                            }
                        """)
                        
                        if fps_value > 0:
                            fps_started = True
                            print(f"  🎬 {Colors.success(f'Modo duas pessoas iniciado! FPS inicial: {fps_value:.2f}')}", flush=True)
                            break
                    except:
                        pass
                    
                    if waited_start % 5 == 0:
                        print(f"  ⏳ {Colors.info(f'Aguardando modo duas pessoas iniciar... ({waited_start}s)')}", flush=True)
                
                if fps_started:
                    # Coletar FPS por 10 segundos (a cada 500ms = 20 amostras)
                    print(f"\n  📊 {Colors.info('Coletando FPS (duas pessoas) durante 10 segundos (a cada 500ms)...')}", flush=True)
                    fps_samples = []
                    
                    for i in range(20):  # 20 amostras a cada 500ms = 10 segundos
                        await page.wait_for_timeout(500)  # Aguardar 500ms entre amostras (mesma frequência da tela)
                        
                        try:
                            fps_from_api = await page.evaluate("""
                                async () => {
                                    try {
                                        const response = await fetch('/api/data_multi');
                                        const data = await response.json();
                                        if (data.pessoas && data.pessoas.length > 0) {
                                            return parseFloat(data.pessoas[0].fps) || 0;
                                        }
                                        return 0;
                                    } catch (e) {
                                        return 0;
                                    }
                                }
                            """)
                            
                            if fps_from_api > 0:
                                fps_samples.append(fps_from_api)
                                # Mostrar progresso a cada 2 segundos (4 amostras)
                                if (i + 1) % 4 == 0:
                                    elapsed_seconds = (i + 1) * 0.5
                                    current_avg = sum(fps_samples) / len(fps_samples) if fps_samples else 0
                                    print(f"    📈 {Colors.info(f'[{elapsed_seconds:.1f}s/10s] FPS atual: {fps_from_api:.2f} | Média: {current_avg:.2f}')}", flush=True)
                        except:
                            pass
                    
                    if fps_samples:
                        avg_fps = sum(fps_samples) / len(fps_samples)
                        max_fps = max(fps_samples)
                        min_fps = min(fps_samples)
                        print(f"\n  📊 {Colors.success('Métricas de FPS coletadas (duas pessoas):')}", flush=True)
                        print(f"    • Amostras: {Colors.cyan(f'{len(fps_samples)} (coletadas a cada 500ms em 10s)')}", flush=True)
                        print(f"    • Média: {Colors.cyan(f'{avg_fps:.2f} FPS')}", flush=True)
                        print(f"    • Máximo: {Colors.green(f'{max_fps:.2f} FPS')}", flush=True)
                        print(f"    • Mínimo: {Colors.yellow(f'{min_fps:.2f} FPS')}", flush=True)
                    
            except Exception as e:
                print(f"  ⚠️ {Colors.warning(f'Erro ao coletar FPS do modo duas pessoas: {e}')}", flush=True)
        
        # Para páginas com streaming de vídeo (contador, contador_multi, contador_video),
        # medir o tráfego acumulado usando múltiplas abordagens
        streaming_traffic = 0
        if page_name in ["/contador", "/contador_multi", "/contador_video"]:
            try:
                # Método 1: Usar Performance API para obter bytes transferidos
                # Isso funciona melhor para recursos estáticos, mas também captura parte do streaming
                network_data = await page.evaluate("""
                    () => {
                        const entries = performance.getEntriesByType('resource');
                        let totalBytes = 0;
                        entries.forEach(entry => {
                            // Para streaming, tentar usar transferSize primeiro
                            if (entry.transferSize && entry.transferSize > 0) {
                                totalBytes += entry.transferSize;
                            } else if (entry.decodedBodySize && entry.decodedBodySize > 0) {
                                // Fallback para decodedBodySize
                                totalBytes += entry.decodedBodySize;
                            } else if (entry.encodedBodySize && entry.encodedBodySize > 0) {
                                // Último fallback
                                totalBytes += entry.encodedBodySize;
                            }
                        });
                        return totalBytes;
                    }
                """)
                
                if network_data and network_data > total_data_downloaded:
                    # Se Performance API retornou mais dados, usar esse valor
                    # (pode incluir dados de streaming)
                    streaming_traffic = network_data - total_data_downloaded
                    total_data_downloaded = network_data
                elif network_data and network_data > 0:
                    # Se Performance API retornou dados mas menos que o que já temos,
                    # pode ser que já estejamos capturando corretamente
                    # Mas vamos usar o maior valor
                    total_data_downloaded = max(total_data_downloaded, network_data)
                
            except Exception as e:
                # Se houver erro, continuar sem o tráfego adicional de streaming
                pass
        
        # Obter tempo de carregamento do DOM via JavaScript
        dom_load_time = await page.evaluate("""
            () => {
                const timing = performance.timing;
                return timing.domContentLoadedEventEnd - timing.navigationStart;
            }
        """)
        
        # Obter memória do navegador via Performance API (se disponível)
        browser_memory_mb = 0.0
        try:
            browser_memory_data = await page.evaluate("""
                () => {
                    if (performance.memory) {
                        return {
                            used: performance.memory.usedJSHeapSize / 1024 / 1024,  // MB
                            total: performance.memory.totalJSHeapSize / 1024 / 1024,  // MB
                            limit: performance.memory.jsHeapSizeLimit / 1024 / 1024   // MB
                        };
                    }
                    return null;
                }
            """)
            if browser_memory_data:
                browser_memory_mb = browser_memory_data.get('used', 0.0)
        except:
            # Performance API não disponível (Chrome/Chromium apenas)
            pass
        
        # Converter bytes para KB
        total_data_kb = total_data_downloaded / 1024
        
        # Calcular métricas de memória e CPU para esta página
        # Usar o tempo atual como fim do período de observação para capturar todo o processamento
        page_start_time = start_navigation
        current_time = time.time()
        
        # Garantir período mínimo de observação de 3 segundos para páginas simples
        # ou usar o tempo total já decorrido para páginas com processamento longo
        time_elapsed = current_time - start_navigation
        min_observation_time = 3.0  # Mínimo de 3 segundos de observação
        
        if time_elapsed < min_observation_time:
            # Para páginas que carregaram muito rápido, aguardar um pouco mais
            remaining_time = min_observation_time - time_elapsed
            await page.wait_for_timeout(int(remaining_time * 1000))
            page_end_time = time.time()
        else:
            # Para páginas com processamento longo (contador_video, etc), já temos tempo suficiente
            page_end_time = current_time
        
        # Filtrar métricas do sistema durante o período de observação da página
        page_system_metrics = [
            m for m in self.system_metrics 
            if page_start_time <= m.timestamp <= page_end_time
        ]
        
        if page_system_metrics and len(page_system_metrics) > 0:
            # Se tiver múltiplas amostras, calcular estatísticas
            memory_values = [m.memory_mb for m in page_system_metrics]
            avg_memory = sum(memory_values) / len(memory_values)
            avg_cpu = sum(m.cpu_percent for m in page_system_metrics) / len(page_system_metrics)
            max_memory = max(memory_values)
            min_memory = min(memory_values)
            
            # Calcular métricas do Flask (se disponível)
            flask_memory_values = [m.flask_memory_mb for m in page_system_metrics if m.flask_memory_mb > 0]
            if flask_memory_values:
                avg_flask_memory = sum(flask_memory_values) / len(flask_memory_values)
                max_flask_memory = max(flask_memory_values)
            else:
                avg_flask_memory = 0.0
                max_flask_memory = 0.0
        else:
            # Fallback para métricas atuais se não houver amostras
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            avg_memory = max_memory = min_memory = memory_mb
            avg_cpu = psutil.cpu_percent()
            
            # Tentar obter memória do Flask no fallback também
            flask_proc = self.find_flask_process()
            if flask_proc:
                try:
                    flask_memory_mb = flask_proc.memory_info().rss / 1024 / 1024
                    avg_flask_memory = max_flask_memory = flask_memory_mb
                except:
                    avg_flask_memory = max_flask_memory = 0.0
            else:
                avg_flask_memory = max_flask_memory = 0.0
        
        return PageMetrics(
            name=page_name,
            load_time=load_time,
            dom_load_time=dom_load_time,
            total_data_downloaded=total_data_kb,
            http_requests_count=http_requests_count,
            avg_memory_mb=avg_memory,
            avg_cpu_percent=avg_cpu,
            max_memory_mb=max_memory,
            min_memory_mb=min_memory,
            avg_flask_memory_mb=avg_flask_memory,
            max_flask_memory_mb=max_flask_memory,
            browser_memory_mb=browser_memory_mb,
            avg_fps=avg_fps
        )
    
    async def run_performance_test(self):
        """
        Executa o teste completo de performance.
        
        Navega por todas as páginas configuradas, coleta métricas
        e coordena todo o processo de teste automatizado.
        """
        Colors.print_header("TESTE DE PERFORMANCE DE REDE E MEMÓRIA")
        
        print(f"\n{Colors.info(f'URL base: {self.base_url}')}", flush=True)
        pages_str = ', '.join(self.pages_to_test)
        print(f"{Colors.info(f'Páginas a testar: {pages_str}')}", flush=True)
        
        self.start_time = time.time()
        self.start_system_monitoring()
        
        async with async_playwright() as p:
            # Configurar navegador
            browser = await p.chromium.launch(headless=False)  # headless=False para visualização no navegador
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Testar cada página
                for page_name in self.pages_to_test:
                    try:
                        # Para contador_video, não pular linha antes
                        if page_name == "/contador_video":
                            print(f"{Colors.info(f'Navegando para: {self.base_url}{page_name}')}", flush=True)
                        else:
                            print(f"\n{Colors.info(f'Navegando para: {self.base_url}{page_name}')}", flush=True)
                        metrics = await self.collect_page_metrics(page, page_name)
                        self.page_metrics.append(metrics)
                        
                        # Mostrar mensagem de carregamento apenas se não for /contador, /contador_multi ou /contador_video (já foram mostradas antes)
                        if page_name != "/contador" and page_name != "/contador_multi" and page_name != "/contador_video":
                            print(f"  ✅ {Colors.success(f'Página {page_name} carregada em {metrics.load_time:.2f}s')}", flush=True)
                        
                        # Exibir métricas imediatamente após cada página
                        self.print_page_metrics_immediate(metrics)
                        
                        # Aguardar entre páginas para estabilizar métricas
                        await page.wait_for_timeout(1000)
                        
                    except Exception as e:
                        print(f"  ❌ {Colors.error(f'Erro ao testar {page_name}: {e}')}", flush=True)
                        continue
                
            finally:
                await browser.close()
        
        self.stop_system_monitoring()
        self.end_time = time.time()
        
        print(f"\n{Colors.success(f'Teste concluído em {self.get_total_execution_time():.2f} segundos!')}", flush=True)
    
    def print_page_metrics_immediate(self, metrics: PageMetrics):
        """
        Exibe métricas de uma página imediatamente após o teste.
        
        Args:
            metrics: Métricas da página testada
        """
        print(f"\n  {Colors.highlight('📊 Métricas da Página:')}", flush=True)
        page_display = metrics.name if metrics.name != "/" else "Index"
        print(f"    • Página: {Colors.bold(page_display)}", flush=True)
        print(f"    • Tempo de Carregamento: {Colors.cyan(f'{metrics.load_time:.2f}s')}", flush=True)
        print(f"    • DOM Load: {Colors.cyan(f'{metrics.dom_load_time:.0f}ms')}", flush=True)
        print(f"    • Dados Baixados: {Colors.green(f'{metrics.total_data_downloaded:.2f} KB')}", flush=True)
        print(f"    • Requisições HTTP: {Colors.yellow(f'{metrics.http_requests_count}')}", flush=True)
        print(f"    • Memória (Teste): {Colors.blue(f'{metrics.avg_memory_mb:.1f} MB')} (média) | {Colors.red(f'{metrics.max_memory_mb:.1f} MB')} (máx) | {Colors.success(f'{metrics.min_memory_mb:.1f} MB')} (mín)", flush=True)
        if metrics.avg_flask_memory_mb > 0:
            print(f"    • Memória (Flask): {Colors.blue(f'{metrics.avg_flask_memory_mb:.1f} MB')} (média) | {Colors.red(f'{metrics.max_flask_memory_mb:.1f} MB')} (máx)", flush=True)
        if metrics.browser_memory_mb > 0:
            print(f"    • Memória (Navegador): {Colors.cyan(f'{metrics.browser_memory_mb:.1f} MB')}", flush=True)
        print(f"    • CPU Médio: {Colors.magenta(f'{metrics.avg_cpu_percent:.1f}%')}", flush=True)
        if metrics.avg_fps > 0:
            print(f"    • FPS Médio: {Colors.cyan(f'{metrics.avg_fps:.2f}')}", flush=True)
        print(flush=True)  # Linha em branco para separação
    
    def get_total_execution_time(self) -> float:
        """
        Calcula o tempo total de execução do teste.
        
        Returns:
            float: Tempo total em segundos
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """
        Gera estatísticas resumidas de todo o teste.
        
        Calcula médias, máximos, mínimos e totais das métricas
        coletadas durante a execução.
        
        Returns:
            Dict[str, Any]: Dicionário com estatísticas consolidadas
        """
        if not self.page_metrics:
            return {}
        
        # Calcular estatísticas de memória
        all_memory_values = [m.avg_memory_mb for m in self.page_metrics]
        memory_stats = {
            'avg': sum(all_memory_values) / len(all_memory_values),
            'max': max(all_memory_values),
            'min': min(all_memory_values)
        }
        
        # Calcular estatísticas de CPU
        all_cpu_values = [m.avg_cpu_percent for m in self.page_metrics]
        cpu_stats = {
            'avg': sum(all_cpu_values) / len(all_cpu_values)
        }
        
        # Calcular estatísticas de rede
        total_network_data = sum(m.total_data_downloaded for m in self.page_metrics)
        heaviest_page = max(self.page_metrics, key=lambda x: x.total_data_downloaded)
        
        return {
            'total_execution_time': self.get_total_execution_time(),
            'memory_stats': memory_stats,
            'cpu_stats': cpu_stats,
            'total_network_data_kb': total_network_data,
            'heaviest_page': heaviest_page.name,
            'pages_tested': len(self.page_metrics)
        }
    
    def print_terminal_report(self):
        """
        Exibe relatório formatado no terminal.
        
        Cria uma apresentação visual das métricas coletadas
        usando tabelas, cards e formatação colorida.
        """
        Colors.print_header("RELATÓRIO DE PERFORMANCE - ANÁLISE DE REDE E MEMÓRIA")
        
        stats = self.generate_summary_stats()
        
        # Cards de resumo
        print(f"\n{Colors.bold(Colors.highlight('RESUMO EXECUTIVO'))}")
        Colors.print_card("Tempo Total", f"{stats['total_execution_time']:.2f} segundos", "⏱️", Colors.CYAN)
        Colors.print_card("Memória Média", f"{stats['memory_stats']['avg']:.2f} MB", "🧠", Colors.BLUE)
        Colors.print_card("CPU Médio", f"{stats['cpu_stats']['avg']:.1f}%", "🖥️", Colors.MAGENTA)
        Colors.print_card("Dados Baixados", f"{stats['total_network_data_kb']:.1f} KB", "🌐", Colors.GREEN)
        
        # Seção de memória detalhada
        Colors.print_section("ANÁLISE DE MEMÓRIA")
        Colors.print_card("Média", f"{stats['memory_stats']['avg']:.2f} MB", "", Colors.CYAN)
        Colors.print_card("Pico Máximo", f"{stats['memory_stats']['max']:.2f} MB", "", Colors.RED)
        Colors.print_card("Valor Mínimo", f"{stats['memory_stats']['min']:.2f} MB", "", Colors.GREEN)
        
        # Tabela de tráfego de rede
        Colors.print_section("TRÁFEGO DE REDE POR PÁGINA")
        headers = ["Página", "Tamanho", "Tempo (s)", "Requests"]
        widths = [20, 15, 12, 10]
        Colors.print_table_header(headers, widths)
        
        for i, metrics in enumerate(self.page_metrics):
            page_display = metrics.name if metrics.name != "/" else "Index"
            colors = [Colors.WHITE, Colors.CYAN, Colors.YELLOW, Colors.GREEN]
            Colors.print_table_row([
                page_display,
                f"{metrics.total_data_downloaded:.2f} KB",
                f"{metrics.load_time:.2f}",
                str(metrics.http_requests_count)
            ], widths, colors)
        
        Colors.print_table_footer(widths)
        
        # Página com maior consumo
        Colors.print_section("PÁGINA COM MAIOR CONSUMO DE REDE")
        heaviest_page = max(self.page_metrics, key=lambda x: x.total_data_downloaded)
        heaviest_display = heaviest_page.name if heaviest_page.name != "/" else "Index"
        Colors.print_card("Página", heaviest_display, "🏆", Colors.YELLOW)
        Colors.print_card("Tamanho Total", f"{heaviest_page.total_data_downloaded:.2f} KB", "🌐", Colors.RED)
        
        Colors.print_header("FIM DO RELATÓRIO")
    
    def save_json_report(self):
        """
        Salva relatório completo em formato JSON.
        
        Exporta todas as métricas coletadas em formato estruturado
        para análise posterior ou integração com outras ferramentas.
        """
        report_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'total_execution_time': self.get_total_execution_time(),
                'base_url': self.base_url,
                'pages_tested': [p.name for p in self.page_metrics]
            },
            'summary_stats': self.generate_summary_stats(),
            'page_metrics': [asdict(m) for m in self.page_metrics],
            'system_metrics': [asdict(m) for m in self.system_metrics]
        }
        
        json_path = os.path.join(self.reports_dir, "network_memory_report.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ {Colors.success(f'Relatório JSON salvo em: {json_path}')}")
    
    def create_performance_chart(self):
        """
        Cria gráficos de performance em formato PNG.
        
        Gera visualizações dos dados coletados usando matplotlib,
        incluindo gráficos de linha para métricas temporais e
        gráficos de barras para comparações entre páginas.
        """
        if not self.system_metrics:
            print(Colors.warning("[AVISO] Nenhuma metrica de sistema disponivel para grafico"))
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Análise de Performance - Métricas do Sistema', fontsize=16, fontweight='bold')
        
        # Converter timestamps para datetime
        timestamps = [datetime.fromtimestamp(m.timestamp) for m in self.system_metrics]
        
        # Gráfico 1: Uso de Memória ao Longo do Tempo
        ax1.plot(timestamps, [m.memory_mb for m in self.system_metrics], 
                color='blue', linewidth=2, marker='o', markersize=3)
        ax1.set_title('Uso de Memória ao Longo do Tempo', fontweight='bold')
        ax1.set_ylabel('Memória (MB)')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        # Gráfico 2: Uso de CPU ao Longo do Tempo
        ax2.plot(timestamps, [m.cpu_percent for m in self.system_metrics], 
                color='red', linewidth=2, marker='s', markersize=3)
        ax2.set_title('Uso de CPU ao Longo do Tempo', fontweight='bold')
        ax2.set_ylabel('CPU (%)')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        # Gráfico 3: Tráfego de Rede por Página (Barras)
        if self.page_metrics:
            page_names = [m.name for m in self.page_metrics]
            network_data = [m.total_data_downloaded for m in self.page_metrics]
            
            bars = ax3.bar(range(len(page_names)), network_data, 
                          color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
            ax3.set_title('Tráfego de Rede por Página', fontweight='bold')
            ax3.set_ylabel('Dados Baixados (KB)')
            ax3.set_xticks(range(len(page_names)))
            ax3.set_xticklabels(page_names, rotation=45, ha='right')
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, network_data):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 4: DOM Load por Página
        if self.page_metrics:
            # Converter DOM Load de milissegundos para segundos
            dom_load_times = [m.dom_load_time / 1000.0 for m in self.page_metrics]
            
            bars = ax4.bar(range(len(page_names)), dom_load_times, 
                          color=['#FF9F43', '#10AC84', '#5F27CD', '#00D2D3'])
            ax4.set_title('DOM Load por Página', fontweight='bold')
            ax4.set_ylabel('Tempo (segundos)')
            ax4.set_xticks(range(len(page_names)))
            ax4.set_xticklabels(page_names, rotation=45, ha='right')
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, dom_load_times):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                        f'{value:.3f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Salvar gráfico
        chart_path = os.path.join(self.reports_dir, "performance_chart.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n📊 {Colors.success(f'Relatório gráfico salvo em: {chart_path}')}")
    
    def generate_html_report(self):
        """
        Gera relatório HTML interativo completo.
        
        Cria uma página web com visualizações interativas,
        tabelas ordenáveis e funcionalidades de exportação.
        Inclui CSS responsivo e JavaScript para interatividade.
        """
        stats = self.generate_summary_stats()
        
        # Calcular estatísticas adicionais para insights
        heaviest_page = max(self.page_metrics, key=lambda x: x.total_data_downloaded)
        fastest_page = min(self.page_metrics, key=lambda x: x.dom_load_time)
        slowest_page = max(self.page_metrics, key=lambda x: x.dom_load_time)
        highest_cpu = max(self.page_metrics, key=lambda x: x.avg_cpu_percent)
        # Priorizar memória do Flask se disponível, senão usar memória do teste
        highest_memory = max(self.page_metrics, 
                           key=lambda x: x.avg_flask_memory_mb if x.avg_flask_memory_mb > 0 else x.avg_memory_mb)
        pages_with_fps = [m for m in self.page_metrics if m.avg_fps > 0]
        best_fps_page = max(pages_with_fps, key=lambda x: x.avg_fps) if pages_with_fps else None
        worst_fps_page = min(pages_with_fps, key=lambda x: x.avg_fps) if pages_with_fps else None
        
        # Preparar dados para tabela
        table_rows = ""
        for metrics in self.page_metrics:
            fps_display = f"{metrics.avg_fps:.2f}" if metrics.avg_fps > 0 else "-"
            flask_memory_display = f"{metrics.avg_flask_memory_mb:.1f} MB" if metrics.avg_flask_memory_mb > 0 else "-"
            flask_max_display = f"{metrics.max_flask_memory_mb:.1f} MB" if metrics.max_flask_memory_mb > 0 else "-"
            browser_memory_display = f"{metrics.browser_memory_mb:.1f} MB" if metrics.browser_memory_mb > 0 else "-"
            table_rows += f"""
            <tr>
                <td>{metrics.name}</td>
                <td>{metrics.load_time:.2f}s</td>
                <td>{metrics.dom_load_time:.0f}ms</td>
                <td>{metrics.total_data_downloaded:.1f} KB</td>
                <td>{metrics.http_requests_count}</td>
                <td>{metrics.avg_memory_mb:.1f} MB</td>
                <td>{metrics.max_memory_mb:.1f} MB</td>
                <td>{metrics.min_memory_mb:.1f} MB</td>
                <td>{flask_memory_display}</td>
                <td>{flask_max_display}</td>
                <td>{browser_memory_display}</td>
                <td>{metrics.avg_cpu_percent:.1f}%</td>
                <td>{fps_display}</td>
            </tr>
            """
        
        # Construir seção de insights detalhada
        fps_section = ""
        if pages_with_fps:
            avg_fps = sum([m.avg_fps for m in pages_with_fps]) / len(pages_with_fps)
            diff_percent = ((best_fps_page.avg_fps - worst_fps_page.avg_fps) / worst_fps_page.avg_fps * 100) if best_fps_page and worst_fps_page else 0
            fps_high = [m.name for m in pages_with_fps if m.avg_fps > 15]
            fps_low = [m.name for m in pages_with_fps if m.avg_fps <= 15]
            
            fps_high_html = f'<li><strong>Páginas com FPS &gt; 15:</strong> {" ".join(fps_high)} <span class="insight-stat">Performance excelente</span></li>' if fps_high else ''
            fps_low_html = f'<li><strong>Páginas com FPS &lt; 15:</strong> {" ".join(fps_low)} <span class="insight-stat">Requer otimização</span></li>' if fps_low else ''
            
            fps_section = f'''
                    <div class="insight-category">
                        <h3>🎬 Análise de Performance de Vídeo (FPS)</h3>
                        <div class="insight-highlight">
                            <strong>Melhor Performance de FPS</strong>
                            <span class="insight-stat">{best_fps_page.name}</span> com {best_fps_page.avg_fps:.2f} FPS
                        </div>
                        <div class="insight-highlight">
                            <strong>Menor Performance de FPS</strong>
                            <span class="insight-stat">{worst_fps_page.name}</span> com {worst_fps_page.avg_fps:.2f} FPS
                        </div>
                        <ul>
                            <li><strong>Média geral de FPS:</strong> {avg_fps:.2f} FPS <span class="insight-stat">{len(pages_with_fps)} páginas com processamento</span></li>
                            <li><strong>Diferença de performance:</strong> {diff_percent:.1f}% superior na melhor página</li>
                            {fps_high_html}
                            {fps_low_html}
                        </ul>
                    </div>
                    '''
        
        # Construir recomendações baseadas nos dados coletados
        # Inicializa uma lista vazia para armazenar as recomendações em formato HTML
        recommendations = []
        
        # Recomendação 1: Análise de tráfego de rede
        # Verifica se a página mais pesada consome mais de 50 KB de dados
        if heaviest_page.total_data_downloaded > 50:
            # Se sim, adiciona recomendação para otimizar (comprimir recursos, lazy loading)
            recommendations.append(f'<li><strong>Otimização de rede recomendada:</strong> A página {heaviest_page.name} consome {heaviest_page.total_data_downloaded:.1f} KB. Considere comprimir recursos ou usar lazy loading.</li>')
        else:
            # Se não, elogia o baixo consumo de dados
            recommendations.append('<li><strong>Tráfego de rede:</strong> Todas as páginas apresentam baixo consumo de dados, excelente!</li>')
        
        # Recomendação 2: Análise de performance de CPU
        # Verifica se alguma página usa mais de 40% de CPU em média
        if highest_cpu.avg_cpu_percent > 40:
            # Se sim, sugere otimização de processamento ou uso de Web Workers
            recommendations.append(f'<li><strong>Performance de CPU:</strong> A página {highest_cpu.name} apresenta alto consumo ({highest_cpu.avg_cpu_percent:.1f}%). Considere otimizar processamento ou usar Web Workers.</li>')
        else:
            # Se não, confirma que o uso está dentro de limites aceitáveis
            recommendations.append('<li><strong>Performance de CPU:</strong> Uso de CPU está dentro de limites aceitáveis em todas as páginas.</li>')
        
        # Recomendação 3: Análise de gestão de memória
        # Usa memória do Flask se disponível, senão usa memória do teste
        if highest_memory.avg_flask_memory_mb > 0:
            # Se Flask está sendo monitorado, usar métricas do Flask
            mem_variation = highest_memory.max_flask_memory_mb - highest_memory.avg_flask_memory_mb
            if mem_variation > 5:
                recommendations.append(f'<li><strong>Gestão de memória (Flask):</strong> Monitorar variação de {mem_variation:.1f} MB em {highest_memory.name}. Verificar possível vazamento de memória.</li>')
            else:
                recommendations.append('<li><strong>Gestão de memória (Flask):</strong> Uso de memória estável no servidor Flask, sem sinais de vazamento.</li>')
        else:
            # Fallback para memória do teste
            if (highest_memory.max_memory_mb - highest_memory.min_memory_mb) > 5:
                recommendations.append(f'<li><strong>Gestão de memória:</strong> Monitorar variação de {highest_memory.max_memory_mb - highest_memory.min_memory_mb:.1f} MB em {highest_memory.name}. Verificar possível vazamento de memória.</li>')
            else:
                recommendations.append('<li><strong>Gestão de memória:</strong> Uso de memória estável em todas as páginas, sem sinais de vazamento.</li>')
        
        # Recomendação 4: Análise de FPS (apenas se houver páginas com processamento de vídeo)
        # Verifica se existe página com FPS e se a pior tem menos de 15 FPS (threshold de performance aceitável)
        if worst_fps_page and worst_fps_page.avg_fps < 15:
            # Se sim, sugere otimização de processamento de vídeo ou redução de qualidade
            recommendations.append(f'<li><strong>Otimização de FPS:</strong> {worst_fps_page.name} apresenta {worst_fps_page.avg_fps:.2f} FPS. Considerar otimizar processamento de vídeo ou reduzir qualidade da detecção.</li>')
        
        # Recomendação 5: Análise de tempo de carregamento (DOM Load)
        # Converte DOM Load de milissegundos para segundos (/1000) e verifica se é maior que 1 segundo
        if slowest_page.dom_load_time / 1000 > 1.0:
            # Se sim, sugere otimização de recursos críticos para melhorar o carregamento
            recommendations.append(f'<li><strong>Carregamento:</strong> A página mais lenta ({slowest_page.name}) leva {slowest_page.dom_load_time/1000:.2f}s (DOM Load). Considerar otimização de recursos críticos.</li>')
        else:
            # Se não, elogia a velocidade de carregamento
            recommendations.append('<li><strong>Carregamento:</strong> Todas as páginas carregam rapidamente, excelente performance!</li>')
        
        # Converte a lista de recomendações em uma string HTML única
        # Junta todos os itens da lista separados por quebras de linha com indentação
        recommendations_html = '\n                            '.join(recommendations)
        
        # Construir strings problemáticas separadamente (evitar backslash em f-strings)
        memory_peak_html = (f'<span class="insight-stat">Pico Flask: {highest_memory.max_flask_memory_mb:.1f} MB</span>' 
                           if highest_memory.max_flask_memory_mb > 0 
                           else f'<span class="insight-stat">Pico: {highest_memory.max_memory_mb:.1f} MB</span>')
        
        # Construir string de variação de memória
        if highest_memory.avg_flask_memory_mb > 0:
            flask_variation = highest_memory.max_flask_memory_mb - highest_memory.avg_flask_memory_mb
            flask_variation_pct = ((flask_variation / highest_memory.avg_flask_memory_mb * 100) 
                                  if highest_memory.avg_flask_memory_mb > 0 else 0)
            memory_variation_html = (f'<li><strong>Variação de memória (Flask):</strong> '
                                     f'{flask_variation:.1f} MB '
                                     f'<span class="insight-stat">{flask_variation_pct:.1f}% de variação</span></li>')
        else:
            test_variation = highest_memory.max_memory_mb - highest_memory.min_memory_mb
            test_variation_pct = ((test_variation / highest_memory.avg_memory_mb * 100) 
                                 if highest_memory.avg_memory_mb > 0 else 0)
            memory_variation_html = (f'<li><strong>Variação de memória:</strong> '
                                    f'{test_variation:.1f} MB '
                                    f'<span class="insight-stat">{test_variation_pct:.1f}% de variação</span></li>')
        
        # Construir string de memória do navegador se disponível
        browser_memory_insight_html = ''
        if any(m.browser_memory_mb > 0 for m in self.page_metrics):
            browser_max_page = max(self.page_metrics, key=lambda x: x.browser_memory_mb)
            browser_max_value = max([m.browser_memory_mb for m in self.page_metrics])
            browser_memory_insight_html = (f'<li><strong>Memória do navegador (maior):</strong> '
                                          f'{browser_max_page.name} '
                                          f'<span class="insight-stat">{browser_max_value:.1f} MB</span></li>')
        
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Performance - Análise de Recursos</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f0f;
            min-height: 100vh;
            padding: 20px;
            color: #ffffff;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            padding: 30px;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
            color: #ffffff;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            color: #a0a0a0;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: transparent;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            text-align: center;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.25);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }}
        
        .card-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
            opacity: 0.9;
        }}
        
        .card-title {{
            font-size: 1.1em;
            color: #a0a0a0;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .card-value {{
            font-size: 2em;
            font-weight: bold;
            color: #ffffff;
        }}
        
        .card-unit {{
            font-size: 0.8em;
            color: #666666;
            margin-left: 5px;
        }}
        
        .content {{
            padding: 30px;
            background: transparent;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #ffffff;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.4);
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: transparent;
        }}
        
        th {{
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        th:hover {{
            background: rgba(255, 255, 255, 0.12);
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }}
        
        tr:hover {{
            background: rgba(255, 255, 255, 0.08);
        }}
        
        .chart-container {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        .insights {{
            background: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 12px;
            border-left: 4px solid rgba(255, 255, 255, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        .insight-category {{
            margin-bottom: 30px;
        }}
        
        .insight-category:last-child {{
            margin-bottom: 0;
        }}
        
        .insight-category h3 {{
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 10px;
        }}
        
        .insight-category h4 {{
            color: #e0e0e0;
            margin-bottom: 12px;
            font-size: 1.1em;
            margin-top: 15px;
        }}
        
        .insight-category ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .insight-category li {{
            margin-bottom: 12px;
            padding-left: 25px;
            position: relative;
            color: #a0a0a0;
            line-height: 1.6;
        }}
        
        .insight-category li:before {{
            content: "▸";
            position: absolute;
            left: 0;
            color: rgba(255, 255, 255, 0.4);
            font-weight: bold;
        }}
        
        .insight-category li strong {{
            color: #ffffff;
        }}
        
        .insight-highlight {{
            background: rgba(255, 255, 255, 0.08);
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 3px solid rgba(255, 255, 255, 0.4);
        }}
        
        .insight-highlight strong {{
            color: #ffffff;
            display: block;
            margin-bottom: 5px;
        }}
        
        .insight-stat {{
            display: inline-block;
            padding: 4px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            margin-left: 8px;
            color: #ffffff;
            font-weight: 600;
        }}
        
        .export-buttons {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 25px;
            margin: 0 10px;
            background: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.15);
            cursor: pointer;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.25);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
        }}
        
        .footer {{
            background: rgba(255, 255, 255, 0.05);
            color: #a0a0a0;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
            border-top: 1px solid rgba(255, 255, 255, 0.15);
        }}
        
        @media (max-width: 768px) {{
            .summary-cards {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
        
        /* Estilos para impressão */
        @media print {{
            * {{
                -webkit-print-color-adjust: exact !important;
                color-adjust: exact !important;
            }}
            
            body {{
                background: white !important;
                padding: 0 !important;
                margin: 0 !important;
                font-size: 12pt !important;
                line-height: 1.4 !important;
            }}
            
            .container {{
                max-width: none !important;
                margin: 0 !important;
                border-radius: 0 !important;
                box-shadow: none !important;
                background: white !important;
            }}
            
            .header {{
                background: #2c3e50 !important;
                color: white !important;
                padding: 15px !important;
                margin-bottom: 10px !important;
                page-break-inside: avoid;
            }}
            
            .header h1 {{
                font-size: 18pt !important;
                margin-bottom: 5px !important;
            }}
            
            .header .subtitle {{
                font-size: 10pt !important;
            }}
            
            .summary-cards {{
                display: block !important;
                padding: 10px !important;
                background: white !important;
                page-break-inside: avoid;
            }}
            
            .card {{
                display: inline-block !important;
                width: 45% !important;
                margin: 5px !important;
                padding: 10px !important;
                border: 1px solid #ddd !important;
                box-shadow: none !important;
                page-break-inside: avoid;
            }}
            
            .card-icon {{
                font-size: 16pt !important;
                margin-bottom: 5px !important;
            }}
            
            .card-title {{
                font-size: 9pt !important;
                margin-bottom: 5px !important;
            }}
            
            .card-value {{
                font-size: 14pt !important;
            }}
            
            .content {{
                padding: 10px !important;
            }}
            
            .section {{
                margin-bottom: 15px !important;
                page-break-inside: avoid;
            }}
            
            .section-title {{
                font-size: 14pt !important;
                margin-bottom: 10px !important;
                padding-bottom: 5px !important;
                border-bottom: 2px solid #3498db !important;
            }}
            
            .table-container {{
                box-shadow: none !important;
                border: 1px solid #ddd !important;
            }}
            
            table {{
                font-size: 10pt !important;
            }}
            
            th {{
                background: #3498db !important;
                color: white !important;
                padding: 8px !important;
                font-size: 9pt !important;
            }}
            
            td {{
                padding: 6px 8px !important;
                font-size: 9pt !important;
            }}
            
            .chart-container {{
                display: none !important;
            }}
            
            .insights {{
                background: #f8f9fa !important;
                padding: 10px !important;
                border-left: 3px solid #27ae60 !important;
                page-break-inside: avoid;
            }}
            
            .insights h3 {{
                font-size: 12pt !important;
                margin-bottom: 8px !important;
            }}
            
            .insights li {{
                font-size: 10pt !important;
                margin-bottom: 5px !important;
            }}
            
            .export-buttons {{
                display: none !important;
            }}
            
            .footer {{
                background: #2c3e50 !important;
                color: white !important;
                padding: 10px !important;
                font-size: 8pt !important;
                page-break-inside: avoid;
            }}
            
            /* Evitar quebras de página desnecessárias */
            .header, .summary-cards, .section {{
                page-break-after: avoid;
            }}
            
            /* Garantir que tabelas não sejam quebradas */
            table {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório de Performance</h1>
            <div class="subtitle">Análise de Recursos do Sistema - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</div>
        </div>
        
        <div class="summary-cards">
            <div class="card">
                <div class="card-icon">⏱️</div>
                <div class="card-title">Tempo Total</div>
                <div class="card-value">{stats['total_execution_time']:.2f}<span class="card-unit">s</span></div>
            </div>
            
            <div class="card">
                <div class="card-icon">💾</div>
                <div class="card-title">Memória Média</div>
                <div class="card-value">{stats['memory_stats']['avg']:.1f}<span class="card-unit">MB</span></div>
            </div>
            
            <div class="card">
                <div class="card-icon">🖥️</div>
                <div class="card-title">CPU Médio</div>
                <div class="card-value">{stats['cpu_stats']['avg']:.1f}<span class="card-unit">%</span></div>
            </div>
            
            <div class="card">
                <div class="card-icon">🌐</div>
                <div class="card-title">Dados Baixados</div>
                <div class="card-value">{stats['total_network_data_kb']:.1f}<span class="card-unit">KB</span></div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2 class="section-title">📋 Métricas Detalhadas por Página</h2>
                <div class="table-container">
                    <table id="metricsTable">
                        <thead>
                            <tr>
                                <th onclick="sortTable(0)">Página</th>
                                <th onclick="sortTable(1)">Tempo Carregamento</th>
                                <th onclick="sortTable(2)">DOM Load</th>
                                <th onclick="sortTable(3)">Dados Baixados</th>
                                <th onclick="sortTable(4)">Requisições</th>
                                <th onclick="sortTable(5)">Memória Teste (Média)</th>
                                <th onclick="sortTable(6)">Memória Teste (Máx)</th>
                                <th onclick="sortTable(7)">Memória Teste (Mín)</th>
                                <th onclick="sortTable(8)">Memória Flask (Média)</th>
                                <th onclick="sortTable(9)">Memória Flask (Máx)</th>
                                <th onclick="sortTable(10)">Memória Navegador</th>
                                <th onclick="sortTable(11)">CPU Médio</th>
                                <th onclick="sortTable(12)">FPS Médio</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">📈 Gráficos de Performance</h2>
                <div class="chart-container">
                    <img src="performance_chart.png" alt="Gráficos de Performance">
                </div>
            </div>
            
            <div class="section">
                <h2 class="section-title">🔍 Insights e Análises</h2>
                <div class="insights">
                    <div class="insight-category">
                        <h3>📊 Resumo Executivo</h3>
                        <div class="insight-highlight">
                            <strong>Tempo Total de Execução</strong>
                            {stats['total_execution_time']:.2f} segundos para testar {stats['pages_tested']} páginas
                            <span class="insight-stat">{stats['total_execution_time']/stats['pages_tested']:.2f}s por página</span>
                        </div>
                        <ul>
                            <li><strong>Média de memória:</strong> {stats['memory_stats']['avg']:.1f} MB <span class="insight-stat">Variação: {stats['memory_stats']['max']-stats['memory_stats']['min']:.1f} MB</span></li>
                            <li><strong>Média de CPU:</strong> {stats['cpu_stats']['avg']:.1f}% <span class="insight-stat">Consumo moderado</span></li>
                            <li><strong>Total de dados transferidos:</strong> {stats['total_network_data_kb']:.1f} KB <span class="insight-stat">({stats['total_network_data_kb']/1024:.2f} MB)</span></li>
                        </ul>
                    </div>
                    
                    <div class="insight-category">
                        <h3>🌐 Análise de Rede e Performance</h3>
                        <div class="insight-highlight">
                            <strong>Página Mais Pesada em Rede</strong>
                            <span class="insight-stat">{heaviest_page.name}</span> com {heaviest_page.total_data_downloaded:.1f} KB baixados
                        </div>
                        <ul>
                            <li><strong>Página mais rápida (DOM Load):</strong> {fastest_page.name} <span class="insight-stat">{fastest_page.dom_load_time/1000:.2f}s</span></li>
                            <li><strong>Página mais lenta (DOM Load):</strong> {slowest_page.name} <span class="insight-stat">{slowest_page.dom_load_time/1000:.2f}s</span></li>
                            <li><strong>Diferença de velocidade:</strong> {((slowest_page.dom_load_time - fastest_page.dom_load_time) / fastest_page.dom_load_time * 100):.1f}% mais lenta</li>
                            <li><strong>Maior número de requisições:</strong> {max(self.page_metrics, key=lambda x: x.http_requests_count).name} <span class="insight-stat">{max([m.http_requests_count for m in self.page_metrics])} requisições</span></li>
                        </ul>
                    </div>
                    
                    <div class="insight-category">
                        <h3>💻 Análise de Recursos do Sistema</h3>
                        <div class="insight-highlight">
                            <strong>Maior Consumo de CPU</strong>
                            <span class="insight-stat">{highest_cpu.name}</span> com {highest_cpu.avg_cpu_percent:.1f}% de uso médio
                        </div>
                        <div class="insight-highlight">
                            <strong>Maior Uso de Memória</strong>
                            <span class="insight-stat">{highest_memory.name}</span> com {highest_memory.avg_flask_memory_mb:.1f} MB (Flask) / {highest_memory.avg_memory_mb:.1f} MB (Teste) médios
                            {memory_peak_html}
                        </div>
                        <ul>
                            {memory_variation_html}
                            <li><strong>Página com menor uso de memória:</strong> {min(self.page_metrics, key=lambda x: x.avg_flask_memory_mb if x.avg_flask_memory_mb > 0 else x.avg_memory_mb).name} <span class="insight-stat">{min([m.avg_flask_memory_mb if m.avg_flask_memory_mb > 0 else m.avg_memory_mb for m in self.page_metrics]):.1f} MB</span></li>
                            <li><strong>Página com menor consumo de CPU:</strong> {min(self.page_metrics, key=lambda x: x.avg_cpu_percent).name} <span class="insight-stat">{min([m.avg_cpu_percent for m in self.page_metrics]):.1f}%</span></li>
                            {browser_memory_insight_html}
                        </ul>
                    </div>
                    
                    {fps_section}
                    
                    <div class="insight-category">
                        <h3>📈 Recomendações e Observações</h3>
                        <ul>
                            {recommendations_html}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="export-buttons">
                <button class="btn" onclick="exportToJSON()">📄 Exportar JSON</button>
                <button class="btn" onclick="exportToCSV()">📊 Exportar CSV</button>
                <button class="btn" onclick="window.print()">🖨️ Imprimir</button>
            </div>
        </div>
        
        <div class="footer">
            <p>Relatório gerado automaticamente pelo sistema de análise de performance</p>
            <p>Desenvolvido com Python, Playwright, psutil e matplotlib</p>
        </div>
    </div>
    
    <script>
        // Função para ordenar tabela
        function sortTable(columnIndex) {{
            const table = document.getElementById('metricsTable');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            const isNumeric = columnIndex > 0; // Colunas 1+ são numéricas
            
            rows.sort((a, b) => {{
                const aVal = a.cells[columnIndex].textContent.trim();
                const bVal = b.cells[columnIndex].textContent.trim();
                
                if (isNumeric) {{
                    return parseFloat(aVal) - parseFloat(bVal);
                }} else {{
                    return aVal.localeCompare(bVal);
                }}
            }});
            
            // Reordenar linhas na tabela
            rows.forEach(row => tbody.appendChild(row));
        }}
        
        // Função para exportar dados como JSON
        function exportToJSON() {{
            const data = {json.dumps([asdict(m) for m in self.page_metrics], indent=2)};
            const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'performance_metrics.json';
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        // Função para exportar dados como CSV
        function exportToCSV() {{
            const table = document.getElementById('metricsTable');
            const rows = Array.from(table.querySelectorAll('tr'));
            
            let csv = '';
            rows.forEach(row => {{
                const cells = Array.from(row.querySelectorAll('th, td'));
                const rowData = cells.map(cell => {{
                    let text = cell.textContent.trim();
                    // Escapar aspas duplas
                    text = text.replace(/"/g, '""');
                    // Envolver em aspas se contém vírgula, aspas ou quebra de linha
                    if (text.includes(',') || text.includes('"') || text.includes('\\n')) {{
                        text = '"' + text + '"';
                    }}
                    return text;
                }}).join(',');
                csv += rowData + '\\n';
            }});
            
            // Adicionar BOM para UTF-8 para garantir encoding correto
            const BOM = '\\uFEFF';
            const blob = new Blob([BOM + csv], {{type: 'text/csv;charset=utf-8'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'performance_metrics.csv';
            a.click();
            URL.revokeObjectURL(url);
        }}
        
        // Adicionar efeitos visuais
        document.addEventListener('DOMContentLoaded', function() {{
            // Animação de entrada para os cards
            const cards = document.querySelectorAll('.card');
            cards.forEach((card, index) => {{
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {{
                    card.style.transition = 'all 0.6s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }}, index * 100);
            }});
        }});
    </script>
</body>
</html>
        """
        
        html_path = os.path.join(self.reports_dir, "network_memory_report.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ {Colors.success(f'Relatório HTML gerado: {html_path}')}")


# =============================================================================
# FUNÇÃO PRINCIPAL E EXECUÇÃO DO SCRIPT
# =============================================================================

async def main():
    """
    Função principal para executar o teste de performance.
    
    Coordena todas as verificações prévias, execução do teste
    e geração de relatórios. Trata erros e fornece feedback ao usuário.
    """
    # Verificar argumentos de linha de comando
    import sys
    skip_confirmation = '--skip-confirmation' in sys.argv or '--yes' in sys.argv or '-y' in sys.argv
    Colors.print_header("TESTE DE PERFORMANCE - DETECTOR DE POLICHINELOS")
    
    print(f"\n{Colors.info('Este script executará uma análise completa de performance da aplicação web,')}")
    print(f"{Colors.info('monitorando rede e uso de memória.')}")
    
    Colors.print_section("INSTRUÇÕES")
    print(f"  1. Certifique-se de que a aplicação Flask está rodando")
    print(f"  2. Execute: python app.py (no diretório detector_polichinelos)")
    print(f"  3. A aplicação deve estar acessível em http://localhost:5000")
    print(f"  4. URLs das páginas:")
    print(f"     • Index: http://localhost:5000/")
    print(f"     • Detector: http://localhost:5000/contador")
    print(f"     • Detector Multi: http://localhost:5000/contador_multi")
    print(f"     • Detector Video: http://localhost:5000/contador_video")
    print(f"  5. Este teste navegará pelas páginas automaticamente")
    
    Colors.print_section("IMPORTANTE")
    print(f"  • O teste abrirá um navegador para visualização")
    print(f"  • Não feche o navegador durante a execução")
    print(f"  • O teste pode levar alguns minutos para completar")
    print(f"  • Relatórios serão salvos em tests/reports/")

    print(flush=True)
    time.sleep(2)  # Aguardar 2 segundos para o usuário ler as instruções
    # Verificar dependências
    if not check_dependencies():
        return
    
    # Verificar navegadores do Playwright
    check_playwright_browsers()
    
    # Verificar aplicação Flask
    if not check_flask_app():
        return
    
    # Pedir confirmação do usuário
    if not skip_confirmation:
        if not ask_user_confirmation():
            print(f"\n{Colors.warning('Teste cancelado pelo usuário.')}")
            return
    else:
        print(f"\n{Colors.info('Confirmação automática ativada. Iniciando teste...')}")
    
    # Criar monitor de performance
    monitor = PerformanceMonitor()
    
    try:
        # Executar teste
        await monitor.run_performance_test()
        
        # Gerar relatórios
        monitor.print_terminal_report()
        monitor.save_json_report()
        monitor.create_performance_chart()
        monitor.generate_html_report()
        
        print(f"\n🎉 {Colors.success('Teste de performance concluído com sucesso!')}")
        print(f"📁 {Colors.info('Verifique os relatórios gerados em tests/reports/')}\n")
        
    except Exception as e:
        print(f"\n❌ {Colors.error(f'Erro durante execução do teste: {e}')}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Executar teste assíncrono
    asyncio.run(main())
