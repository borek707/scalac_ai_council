#!/usr/bin/env python3
"""
Setup script dla Rada AI v2+
Sprawdza wymagania, instaluje zależności, konfiguruje środowisko.

Usage:
    python scripts/setup.py
    python scripts/setup.py --phase 2  # Setup dla Fazy 2
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """Sprawdź wersję Pythona."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9+ wymagany")
        print(f"   Obecna wersja: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_variables():
    """Sprawdź zmienne środowiskowe."""
    required = ["OPENAI_API_KEY"]
    optional = ["SERPAPI_API_KEY", "DATAFORSEO_LOGIN", "DATAFORSEO_PASSWORD"]
    
    print("\n🔑 Zmienne środowiskowe:")
    
    all_good = True
    for var in required:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: BRAK (wymagane)")
            all_good = False
    
    for var in optional:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: ustawione (opcjonalne)")
        else:
            print(f"   ⚠️  {var}: nieustawione (opcjonalne)")
    
    return all_good


def install_dependencies(phase: int):
    """Zainstaluj zależności dla danej fazy."""
    req_files = {
        1: "requirements-v2.txt",
        2: "requirements-v2.5.txt",
        3: "requirements-v3.txt"
    }
    
    req_file = req_files.get(phase, "requirements-v2.txt")
    
    if not os.path.exists(req_file):
        print(f"❌ Nie znaleziono {req_file}")
        return False
    
    print(f"\n📦 Instalacja zależności z {req_file}...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", req_file
        ])
        print(f"   ✅ Zależności zainstalowane")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Błąd instalacji: {e}")
        return False


def setup_directories():
    """Utwórz potrzebne katalogi."""
    dirs = [
        "./chroma_db",
        "./projects",
        "./logs",
        "./cache"
    ]
    
    print("\n📁 Katalogi:")
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {d}")


def create_env_template():
    """Utwórz template .env jeśli nie istnieje."""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"\n⚠️  {env_file} już istnieje")
        return
    
    template = """# Rada AI - Environment Variables

# REQUIRED
OPENAI_API_KEY=sk-...

# OPTIONAL - Phase 2 (Tools)
SERPAPI_API_KEY=...
DATAFORSEO_LOGIN=...
DATAFORSEO_PASSWORD=...

# OPTIONAL - Phase 4 (Enterprise)
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_URL=postgresql://user:pass@localhost/rada
PINECONE_API_KEY=...
PINECONE_ENV=...

# DEVELOPMENT
DEBUG=false
LOG_LEVEL=INFO
"""
    
    with open(env_file, "w") as f:
        f.write(template)
    
    print(f"\n📝 Utworzono {env_file}")
    print("   ⚠️  Edytuj plik i dodaj swoje klucze API!")


def test_imports(phase: int):
    """Przetestuj importy."""
    print("\n🧪 Testowanie importów:")
    
    imports_to_test = [
        ("langchain", "LangChain"),
        ("chromadb", "ChromaDB"),
        ("openai", "OpenAI"),
    ]
    
    if phase >= 2:
        imports_to_test.extend([
            ("redis", "Redis"),
            ("httpx", "HTTPX"),
        ])
    
    if phase >= 3:
        imports_to_test.append(("langgraph", "LangGraph"))
    
    all_good = True
    for module, name in imports_to_test:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}")
            all_good = False
    
    return all_good


def main():
    parser = argparse.ArgumentParser(description='Setup Rada AI')
    parser.add_argument('--phase', type=int, choices=[1, 2, 3], default=1,
                       help='Which phase to setup (1=v2 memory, 2=v2.5 tools, 3=v3 graph)')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency installation')
    parser.add_argument('--create-env', action='store_true',
                       help='Create .env template')
    
    args = parser.parse_args()
    
    print("🚀 Rada AI - Setup")
    print("=" * 50)
    print(f"Faza: {args.phase}")
    print("=" * 50)
    
    # Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Create .env template
    if args.create_env or not os.path.exists(".env"):
        create_env_template()
    
    # Check env variables
    env_ok = check_env_variables()
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies(args.phase):
            print("\n❌ Setup nieudany - problem z zależnościami")
            sys.exit(1)
    
    # Test imports
    if not test_imports(args.phase):
        print("\n❌ Setup nieudany - problem z importami")
        sys.exit(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Setup zakończony sukcesem!")
    print("=" * 50)
    
    if not env_ok:
        print("\n⚠️  UWAGA: Brakuje wymaganych zmiennych środowiskowych!")
        print("   1. Edytuj plik .env")
        print("   2. Dodaj OPENAI_API_KEY")
        print("   3. source .env (lak restartuj terminal)")
    
    print(f"\nNastępne kroki dla Fazy {args.phase}:")
    
    if args.phase == 1:
        print("   1. python scripts/ingest_knowledge.py")
        print("   2. python -m src.v2.orchestrator --project 'Test' --type CORE")
    elif args.phase == 2:
        print("   1. Dodaj SERPAPI_API_KEY do .env")
        print("   2. python scripts/ingest_knowledge.py")
        print("   3. python -m src.v2.orchestrator --project 'Test' --type CORE")
    elif args.phase == 3:
        print("   1. python -m src.v3.orchestrator --project 'Test' --type CORE")
    
    print("\n📖 Dokumentacja:")
    print("   - ROADMAP.md - Ogólny plan")
    print("   - roadmap/PHASE_*.md - Szczegóły faz")
    print("   - roadmap/ARCHITECTURE.md - Architektura")


if __name__ == "__main__":
    main()
