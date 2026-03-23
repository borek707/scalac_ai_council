#!/bin/bash
# Skrypt do wypchnięcia Rady AI na GitHub
# Użycie: ./github-push.sh TWÓJ_USERNAME NAZWA_REPO

USERNAME=$1
REPO_NAME=${2:-"scalac-ai-council"}

if [ -z "$USERNAME" ]; then
    echo "❌ Użycie: ./github-push.sh TWOJ_USERNAME [NAZWA_REPO]"
    echo "Przykład: ./github-push.sh jankowalski scalac-ai-council"
    exit 1
fi

echo "🚀 Wypychanie Rady AI na GitHub..."
echo "Użytkownik: $USERNAME"
echo "Repo: $REPO_NAME"

# Dodaj remote
git remote remove origin 2>/dev/null
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"

# Sprawdź czy działa
echo "🔗 Testowanie połączenia..."
git ls-remote origin >/dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Połączenie działa!"
else
    echo "⚠️  Musisz się zalogować do GitHub (otworzy się okno)..."
fi

# Push
git branch -M main
git push -u origin main

echo ""
echo "✅ Gotowe! Sprawdź: https://github.com/$USERNAME/$REPO_NAME"
