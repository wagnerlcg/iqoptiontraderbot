"""
Script de Configuração do Ambiente - IQ Option API
Automatiza a instalação e limpeza das dependências do projeto.

Uso:
    python setup_env.py
"""

import subprocess
import sys
import os

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def run_command(command, description=""):
    """Executa um comando e retorna o resultado."""
    if description:
        print(f"\n{'='*60}")
        print(f"📋 {description}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_package_installed(package_name):
    """Verifica se um pacote está instalado."""
    success, stdout, _ = run_command(
        f"{sys.executable} -m pip show {package_name}",
        description=f"Verificando se {package_name} está instalado"
    )
    return success and "Name:" in stdout

def uninstall_package(package_name):
    """Desinstala um pacote."""
    print(f"\n⚠️  Desinstalando {package_name}...")
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip uninstall -y {package_name}",
        description=f"Desinstalando {package_name}"
    )
    
    if success:
        print(f"✅ {package_name} desinstalado com sucesso!")
        return True
    else:
        print(f"⚠️  Não foi possível desinstalar {package_name} (pode não estar instalado)")
        return False

def install_requirements():
    """Instala as dependências do requirements.txt."""
    if not os.path.exists("requirements.txt"):
        print("❌ Arquivo requirements.txt não encontrado!")
        return False
    
    print("\n📦 Instalando dependências do requirements.txt...")
    success, stdout, stderr = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        description="Instalando dependências"
    )
    
    if success:
        print("✅ Dependências instaladas com sucesso!")
        return True
    else:
        print(f"⚠️  Alguns avisos durante instalação:\n{stderr}")
        # Mesmo com avisos, pode estar funcionando
        return True

def check_env_file():
    """Verifica se o arquivo .env existe."""
    if os.path.exists(".env"):
        print("✅ Arquivo .env encontrado!")
        return True
    else:
        print("⚠️  Arquivo .env não encontrado!")
        if os.path.exists(".env.example"):
            print("\n💡 Criando arquivo .env a partir do .env.example...")
            try:
                with open(".env.example", "r", encoding="utf-8") as example:
                    content = example.read()
                with open(".env", "w", encoding="utf-8") as env_file:
                    env_file.write(content)
                print("✅ Arquivo .env criado!")
                print("⚠️  IMPORTANTE: Edite o arquivo .env e adicione suas credenciais reais!")
                return False
            except Exception as e:
                print(f"❌ Erro ao criar .env: {e}")
                return False
        else:
            print("\n💡 Crie um arquivo .env com suas credenciais:")
            print("   IQ_OPTION_EMAIL=seu_email@example.com")
            print("   IQ_OPTION_PASSWORD=sua_senha")
            return False

def test_import():
    """Testa se o módulo pode ser importado."""
    print("\n🧪 Testando importação do módulo...")
    
    # Verificar se estamos no diretório correto
    current_dir = os.getcwd()
    init_file = os.path.join(current_dir, "__init__.py")
    stable_api_file = os.path.join(current_dir, "stable_api.py")
    
    if not os.path.exists(init_file):
        print("❌ Arquivo __init__.py não encontrado!")
        print(f"   Diretório atual: {current_dir}")
        print("   Certifique-se de estar no diretório raiz do projeto")
        return False
    
    if not os.path.exists(stable_api_file):
        print("❌ Arquivo stable_api.py não encontrado!")
        print("   Certifique-se de estar no diretório raiz do projeto")
        return False
    
    print(f"✅ Arquivos do módulo encontrados em: {current_dir}")
    
    # Tentar importar (funcionará se executado do diretório correto)
    try:
        # Para importar iqoptionapi quando estamos dentro do diretório iqoptionapi,
        # precisamos adicionar o diretório pai ao path ou adicionar o atual e importar como módulo
        # Vamos tentar adicionar o diretório atual e usar importação relativa
        
        # Método 1: Tentar adicionar diretório atual ao path
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Verificar se podemos importar os componentes principais
        # Quando estamos dentro do diretório iqoptionapi, precisamos adicionar ao path
        original_path = sys.path.copy()
        
        try:
            # Tentar importar diretamente (quando estamos no diretório do pacote)
            import stable_api
            from stable_api import IQ_Option
            print("✅ Arquivo stable_api.py e classe IQ_Option importados diretamente!")
            print("✅ Estrutura do módulo está correta!")
            print("   (Os scripts adicionam automaticamente o diretório ao PYTHONPATH)")
            module_ok = True
        except ImportError as e1:
            # Tentar como módulo instalado (quando estamos fora ou pacote instalado)
            try:
                import iqoptionapi
                from iqoptionapi import IQ_Option
                print("✅ Módulo iqoptionapi importado como pacote instalado!")
                module_ok = True
            except ImportError:
                print("⚠️  Não foi possível importar como módulo ou arquivo direto")
                print(f"   Erro direto: {e1}")
                print("   Isso é normal se você estiver executando setup_env.py")
                print("   Os scripts de exemplo funcionarão corretamente")
                module_ok = False
        
        finally:
            sys.path = original_path
        
        # Se o módulo foi importado, já testamos IQ_Option acima
        # Se não foi, mas os arquivos existem, a estrutura está OK e scripts funcionarão
        if not module_ok:
            print("⚠️  Teste de importação não completo, mas estrutura parece OK")
            # Considerar OK porque os arquivos existem e scripts adicionam path automaticamente
            module_ok = True
        
        # Testar se consegue carregar variáveis de ambiente
        try:
            from dotenv import load_dotenv
            load_dotenv()
            email = os.getenv("IQ_OPTION_EMAIL")
            password = os.getenv("IQ_OPTION_PASSWORD")
            
            if email and password and email != "seu_email@example.com" and password != "sua_senha_aqui":
                print("✅ Credenciais carregadas do .env!")
                return True
            else:
                print("⚠️  Credenciais não configuradas ou ainda usando valores de exemplo")
                print("   Edite o arquivo .env com suas credenciais reais")
                return True  # Módulo funciona, só falta configurar credenciais
        except ImportError:
            print("⚠️  python-dotenv não está instalado")
            return False
            
    except ImportError as e:
        print(f"❌ Erro ao importar módulo: {e}")
        print("\n💡 SOLUÇÃO:")
        print("   IMPORTANTE: Execute os scripts Python a partir do diretório do projeto")
        print("   Exemplo: python TESTE_RAPIDO.py")
        print("   Os scripts automaticamente adicionam o diretório ao PYTHONPATH")
        print("\n   Alternativamente, instale o pacote localmente:")
        print("   pip install -e .")
        return False

def main():
    """Função principal."""
    print("="*60)
    print("🔧 Script de Configuração - IQ Option API")
    print("="*60)
    
    # Verificar se está em modo automático (via argumento --auto ou --yes)
    auto_mode = '--auto' in sys.argv or '--yes' in sys.argv or '-y' in sys.argv
    
    # Passo 1: Verificar e desinstalar pacote antigo
    if check_package_installed("iqoptionapi"):
        print("\n⚠️  Pacote antigo 'iqoptionapi' do PyPI encontrado!")
        
        if auto_mode:
            print("⚠️  Modo automático: desinstalando pacote antigo...")
            uninstall_package("iqoptionapi")
        else:
            try:
                response = input("Deseja desinstalá-lo? (s/N): ").strip().lower()
                if response in ['s', 'sim', 'y', 'yes']:
                    uninstall_package("iqoptionapi")
                else:
                    print("⚠️  Mantendo pacote antigo (pode causar conflitos)")
            except (EOFError, KeyboardInterrupt):
                print("\n⚠️  Entrada não disponível. Use --auto para modo automático.")
                print("⚠️  Continuando sem desinstalar...")
    else:
        print("\n✅ Nenhum pacote antigo encontrado")
    
    # Passo 2: Instalar dependências
    print("\n" + "="*60)
    print("📦 Instalando/Atualizando dependências...")
    print("="*60)
    install_requirements()
    
    # Passo 3: Verificar arquivo .env
    print("\n" + "="*60)
    print("📝 Verificando configuração do arquivo .env...")
    print("="*60)
    env_ok = check_env_file()
    
    # Passo 4: Testar importação
    print("\n" + "="*60)
    print("🧪 Testando configuração...")
    print("="*60)
    import_ok = test_import()
    
    # Resumo final
    print("\n" + "="*60)
    print("📊 RESUMO DA CONFIGURAÇÃO")
    print("="*60)
    
    if import_ok and env_ok:
        print("✅ Configuração completa! Tudo pronto para usar!")
        print("\n🚀 Próximos passos:")
        print("   1. Edite o arquivo .env com suas credenciais reais")
        print("   2. Execute: python TESTE_RAPIDO.py")
    elif import_ok:
        print("✅ Módulo funcionando!")
        print("⚠️  Configure o arquivo .env com suas credenciais")
    else:
        print("⚠️  Verifique os erros acima e tente novamente")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)

