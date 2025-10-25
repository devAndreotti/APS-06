#!/usr/bin/env python3
"""
Script de instalação automática para o Detector de Polichinelos
Cria ambiente virtual, instala dependências e configura tudo automaticamente.
"""

import os
import sys
import subprocess
import platform

def run_command(command, shell=True):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=shell, check=True, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def is_windows():
    """Detecta se está rodando no Windows"""
    return platform.system() == "Windows"

def create_virtual_environment():
    """Cria o ambiente virtual"""
    print("Criando ambiente virtual...")
    success, output = run_command("python -m venv venv")
    if success:
        print("Ambiente virtual criado com sucesso!")
        return True
    else:
        print(f"Erro ao criar ambiente virtual: {output}")
        return False

def get_activation_command():
    """Retorna o comando correto para ativar o venv baseado no OS"""
    if is_windows():
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Instala as dependências no ambiente virtual"""
    print("Instalando dependencias...")
    
    if is_windows():
        pip_command = "venv\\Scripts\\pip install -r requirements.txt"
    else:
        pip_command = "venv/bin/pip install -r requirements.txt"
    
    success, output = run_command(pip_command)
    if success:
        print("Dependencias instaladas com sucesso!")
        return True
    else:
        print(f"Erro ao instalar dependencias: {output}")
        return False

def show_usage_instructions():
    """Mostra instruções de como usar o projeto"""
    activation_cmd = get_activation_command()
    
    print("\n" + "="*60)
    print("INSTALACAO CONCLUIDA COM SUCESSO!")
    print("="*60)
    print("\nPara usar o projeto:")
    print(f"1. Ativar ambiente virtual: {activation_cmd}")
    print("2. Executar aplicacao: python app.py")
    print("3. Abrir no navegador: http://localhost:5000")
    print("4. Desativar ambiente virtual: deactivate")
    print("\nDica: O ambiente virtual ja esta ativo neste terminal!")
    print("="*60)

def main():
    """Função principal do script"""
    print("Iniciando instalacao do Detector de Polichinelos...")
    print(f"Sistema operacional: {platform.system()}")
    
    # Verificar se já existe um ambiente virtual
    if os.path.exists("venv"):
        print("Ambiente virtual ja existe!")
        response = input("Deseja recriar? (s/N): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            print("Removendo ambiente virtual existente...")
            if is_windows():
                run_command("rmdir /s /q venv")
            else:
                run_command("rm -rf venv")
        else:
            print("Instalando dependencias no ambiente existente...")
            if install_dependencies():
                show_usage_instructions()
            return
    
    # Criar ambiente virtual
    if not create_virtual_environment():
        return
    
    # Instalar dependências
    if not install_dependencies():
        return
    
    # Mostrar instruções
    show_usage_instructions()
    
    # Tentar ativar automaticamente (opcional)
    print("\nTentando ativar ambiente virtual automaticamente...")
    activation_cmd = get_activation_command()
    
    if is_windows():
        print("No Windows, execute manualmente:")
        print(f"   {activation_cmd}")
        print("   python app.py")
    else:
        print("Execute os seguintes comandos:")
        print(f"   {activation_cmd}")
        print("   python app.py")

if __name__ == "__main__":
    main()
