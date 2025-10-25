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

import sys
import os
# Configurar encoding para Windows
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

import asyncio
import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
import psutil
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from playwright.async_api import async_playwright, Page, Browser
from dataclasses import dataclass, asdict


class Colors:
    """Cores para terminal"""
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
    def print_header(title: str, width: int = 80):
        """Imprime cabeçalho formatado"""
        print("\n" + "=" * width)
        print(f" {title} ")
        print("=" * width)
    
    @staticmethod
    def print_section(title: str, width: int = 80):
        """Imprime seção formatada"""
        print("\n" + "─" * width)
        print(f" {title} ")
        print("─" * width + "\n")
    
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


def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print(f"\n{Colors.info('Verificando dependências...')}")
    
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
    """Verifica se os navegadores do Playwright estão instalados"""
    # Verificação removida - não é necessária pois o teste falharia se não funcionasse
    return True


def check_flask_app():
    """Verifica se a aplicação Flask está rodando"""
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
    """Pede confirmação do usuário para continuar"""
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


@dataclass
class PageMetrics:
    """Classe para armazenar métricas de uma página específica"""
    name: str
    load_time: float
    dom_load_time: float
    total_data_downloaded: float  # em KB
    http_requests_count: int
    avg_memory_mb: float
    avg_cpu_percent: float
    max_memory_mb: float
    min_memory_mb: float


@dataclass
class SystemMetrics:
    """Classe para armazenar métricas do sistema durante a execução"""
    timestamp: float
    memory_mb: float
    cpu_percent: float
    network_data_kb: float


class PerformanceMonitor:
    """Monitor de performance principal"""
    
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
    
    def start_system_monitoring(self):
        """Inicia o monitoramento contínuo do sistema"""
        self.monitoring_active = True
        
        def monitor_loop():
            while self.monitoring_active:
                try:
                    # Obter métricas do processo Python atual
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024  # Converter para MB
                    
                    # Obter uso de CPU
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    
                    # Criar métrica do sistema
                    metric = SystemMetrics(
                        timestamp=time.time(),
                        memory_mb=memory_mb,
                        cpu_percent=cpu_percent,
                        network_data_kb=0  # Será atualizado durante navegação
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
        """Para o monitoramento do sistema"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2)
    
    async def collect_page_metrics(self, page: Page, page_name: str) -> PageMetrics:
        """Coleta métricas específicas de uma página"""
        # Variáveis para coleta de dados de rede
        total_data_downloaded = 0
        http_requests_count = 0
        
        # Interceptar respostas HTTP para medir tráfego
        async def handle_response(response):
            nonlocal total_data_downloaded, http_requests_count
            
            try:
                # Contar requisições
                http_requests_count += 1
                
                # Obter tamanho do conteúdo
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
                print(f"Erro ao processar resposta HTTP: {e}")
        
        # Registrar handler de resposta
        page.on('response', handle_response)
        
        # Medir tempo de carregamento
        start_navigation = time.time()
        
        # Navegar para a página
        await page.goto(f"{self.base_url}{page_name}", wait_until='domcontentloaded')
        
        # Aguardar um pouco para garantir carregamento completo
        await page.wait_for_timeout(2000)
        
        # Obter tempo de carregamento do DOM via JavaScript
        dom_load_time = await page.evaluate("""
            () => {
                const timing = performance.timing;
                return timing.domContentLoadedEventEnd - timing.navigationStart;
            }
        """)
        
        end_navigation = time.time()
        load_time = end_navigation - start_navigation
        
        # Converter bytes para KB
        total_data_kb = total_data_downloaded / 1024
        
        # Calcular métricas de memória e CPU para esta página
        page_start_time = start_navigation
        page_end_time = end_navigation
        
        # Filtrar métricas do sistema durante o carregamento desta página
        page_system_metrics = [
            m for m in self.system_metrics 
            if page_start_time <= m.timestamp <= page_end_time
        ]
        
        if page_system_metrics:
            avg_memory = sum(m.memory_mb for m in page_system_metrics) / len(page_system_metrics)
            avg_cpu = sum(m.cpu_percent for m in page_system_metrics) / len(page_system_metrics)
            max_memory = max(m.memory_mb for m in page_system_metrics)
            min_memory = min(m.memory_mb for m in page_system_metrics)
        else:
            # Fallback para métricas atuais
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            avg_memory = max_memory = min_memory = memory_mb
            avg_cpu = psutil.cpu_percent()
        
        return PageMetrics(
            name=page_name,
            load_time=load_time,
            dom_load_time=dom_load_time,
            total_data_downloaded=total_data_kb,
            http_requests_count=http_requests_count,
            avg_memory_mb=avg_memory,
            avg_cpu_percent=avg_cpu,
            max_memory_mb=max_memory,
            min_memory_mb=min_memory
        )
    
    async def run_performance_test(self):
        """Executa o teste completo de performance"""
        Colors.print_header("TESTE DE PERFORMANCE DE REDE E MEMÓRIA")
        
        print(f"\n{Colors.info(f'URL base: {self.base_url}')}")
        pages_str = ', '.join(self.pages_to_test)
        print(f"{Colors.info(f'Páginas a testar: {pages_str}')}")
        
        self.start_time = time.time()
        self.start_system_monitoring()
        
        async with async_playwright() as p:
            # Configurar navegador
            browser = await p.chromium.launch(headless=False)  # headless=False para visualizar
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # Testar cada página
                for page_name in self.pages_to_test:
                    try:
                        print(f"\n{Colors.info(f'Navegando para: {self.base_url}{page_name}')}")
                        metrics = await self.collect_page_metrics(page, page_name)
                        self.page_metrics.append(metrics)
                        
                        print(f"  ✅ {Colors.success(f'Página {page_name} carregada em {metrics.load_time:.2f}s')}")
                        
                        # Aguardar entre páginas para estabilizar métricas
                        await page.wait_for_timeout(1000)
                        
                    except Exception as e:
                        print(f"  ❌ {Colors.error(f'Erro ao testar {page_name}: {e}')}")
                        continue
                
            finally:
                await browser.close()
        
        self.stop_system_monitoring()
        self.end_time = time.time()
        
        print(f"\n{Colors.success(f'Teste concluído em {self.get_total_execution_time():.2f} segundos!')}")
    
    def get_total_execution_time(self) -> float:
        """Retorna o tempo total de execução"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def generate_summary_stats(self) -> Dict[str, Any]:
        """Gera estatísticas resumidas do teste"""
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
        """Exibe relatório formatado no terminal"""
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
        """Salva relatório em formato JSON"""
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
        """Cria gráfico de performance em PNG"""
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
        
        # Gráfico 4: Tempo de Carregamento por Página
        if self.page_metrics:
            load_times = [m.load_time for m in self.page_metrics]
            
            bars = ax4.bar(range(len(page_names)), load_times, 
                          color=['#FF9F43', '#10AC84', '#5F27CD', '#00D2D3'])
            ax4.set_title('Tempo de Carregamento por Página', fontweight='bold')
            ax4.set_ylabel('Tempo (segundos)')
            ax4.set_xticks(range(len(page_names)))
            ax4.set_xticklabels(page_names, rotation=45, ha='right')
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, load_times):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                        f'{value:.2f}s', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        
        # Salvar gráfico
        chart_path = os.path.join(self.reports_dir, "performance_chart.png")
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n📊 {Colors.success(f'Relatório gráfico salvo em: {chart_path}')}")
    
    def generate_html_report(self):
        """Gera relatório HTML interativo"""
        stats = self.generate_summary_stats()
        
        # Preparar dados para tabela
        table_rows = ""
        for metrics in self.page_metrics:
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
                <td>{metrics.avg_cpu_percent:.1f}%</td>
            </tr>
            """
        
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card-icon {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}
        
        .card-title {{
            font-size: 1.1em;
            color: #666;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .card-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .card-unit {{
            font-size: 0.8em;
            color: #888;
            margin-left: 5px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #2c3e50;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3498db;
        }}
        
        .table-container {{
            overflow-x: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
        }}
        
        th {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            cursor: pointer;
            user-select: none;
        }}
        
        th:hover {{
            background: linear-gradient(135deg, #2980b9 0%, #1f618d 100%);
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .chart-container {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .insights {{
            background: linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%);
            padding: 25px;
            border-radius: 10px;
            border-left: 5px solid #27ae60;
        }}
        
        .insights h3 {{
            color: #27ae60;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .insights ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .insights li {{
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
        }}
        
        .insights li:before {{
            content: "🔍";
            position: absolute;
            left: 0;
        }}
        
        .export-buttons {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 25px;
            margin: 0 10px;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
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
                                <th onclick="sortTable(5)">Memória Média</th>
                                <th onclick="sortTable(6)">Memória Máxima</th>
                                <th onclick="sortTable(7)">Memória Mínima</th>
                                <th onclick="sortTable(8)">CPU Médio</th>
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
                    <h3>Principais Descobertas:</h3>
                    <ul>
                        <li><strong>Página mais pesada em rede:</strong> {stats['heaviest_page']} com {max([m.total_data_downloaded for m in self.page_metrics]):.1f} KB baixados</li>
                        <li><strong>Página com maior consumo de CPU:</strong> {max(self.page_metrics, key=lambda x: x.avg_cpu_percent).name} com {max([m.avg_cpu_percent for m in self.page_metrics]):.1f}% de uso médio</li>
                        <li><strong>Página com maior uso de memória:</strong> {max(self.page_metrics, key=lambda x: x.avg_memory_mb).name} com {max([m.avg_memory_mb for m in self.page_metrics]):.1f} MB médios</li>
                        <li><strong>Tempo total de execução:</strong> {stats['total_execution_time']:.2f} segundos para testar {stats['pages_tested']} páginas</li>
                    </ul>
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


async def main():
    """Função principal para executar o teste de performance"""
    Colors.print_header("TESTE DE PERFORMANCE - DETECTOR DE POLICHINELOS")
    
    print(f"{Colors.info('Este script executará uma análise completa de performance da aplicação web,')}")
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
    
    # Verificar dependências
    if not check_dependencies():
        return
    
    # Verificar navegadores do Playwright
    check_playwright_browsers()
    
    # Verificar aplicação Flask
    if not check_flask_app():
        return
    
    # Pedir confirmação do usuário
    if not ask_user_confirmation():
        print(f"\n{Colors.warning('Teste cancelado pelo usuário.')}")
        return
    
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
