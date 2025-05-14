# URL Shortener App

Aplikacja do skracania URLi oparta na frameworku **Django** i **Django REST Framework**. Projekt wykorzystuje konteneryzację z użyciem **Docker** i **Docker Compose**. Aplikacja oferuje API do tworzenia, zarządzania i śledzenia skróconych linków.

## Uruchamianie aplikacji

Aby uruchomić aplikację na swoim lokalnym środowisku, wykonaj poniższe kroki:

### 1. **Wymagania wstępne**
   - **Docker** (oraz **Docker Compose**) – używamy Dockera do konteneryzacji aplikacji.
   - **Git** – do klonowania repozytorium.
   - **Python 3.10+** (opcjonalnie, jeśli chcesz uruchomić aplikację lokalnie bez Dockera).

### 2. **Klonowanie repozytorium**
   Klonuj repozytorium do swojego lokalnego środowiska:
   ```bash
   git clone https://github.com/<twoje-imie>/url_shortener.git
   cd url_shortener

