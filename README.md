# Whitefly – Zadanie Rekrutacyjne Python Developer

## Opis projektu

Projekt implementuje aplikację webową w dwóch frameworkach — **Flask** i **FastAPI** — działających za rewersowym proxy **Nginx**, z kolejkowaniem zadań przez **Celery + Redis** oraz bazą danych **PostgreSQL**.

## Struktura projektu

```
Whitefly_1/
├── docs/                          # Zrzuty ekranu z testów wydajnościowych
├── fastapi_app/
│   ├── templates/
│   │   ├── form_async.html
│   │   └── form_sync.html
│   ├── app.py
│   ├── celery_app.py
│   ├── db.py
│   ├── security.py
│   ├── tasks.py
│   ├── Dockerfile
│   └── requirements.txt
├── flask_app/
│   ├── templates/
│   │   ├── form_async.html
│   │   └── form_sync.html
│   ├── app.py
│   ├── celery_app.py
│   ├── db.py
│   ├── security.py
│   ├── tasks.py
│   ├── uwsgi.ini
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/                           # Przygotowane konfiguracje Kubernetes
├── nginx/
│   └── nginx.conf
├── schema.sql
├── docker-compose.yml
├── .env.example
└── .gitignore
```

## Zadania

### Zadanie 1 — Flask
Aplikacja Flask zawierająca:
- `GET /flask/` — strona Hello World
- `GET/POST /flask/form_sync` — formularz synchroniczny zapisujący dane bezpośrednio do PostgreSQL
- `GET/POST /flask/form_async` — formularz asynchroniczny kolejkujący zapis przez Celery + Redis

### Zadanie 2 — FastAPI
Aplikacja FastAPI analogiczna do Zadania 1:
- `GET /fastapi/` — endpoint Hello World
- `GET/POST /fastapi/form_sync` — formularz synchroniczny
- `GET/POST /fastapi/form_async` — formularz asynchroniczny z Celery + Redis

### Zadanie 3 — Wdrożenie, proxy i testy wydajnościowe

Obie aplikacje działają za rewersowym proxy Nginx:
- `/flask/` → aplikacja Flask przez uWSGI (port 5000)
- `/fastapi/` → aplikacja FastAPI przez Uvicorn (port 8000)

Aplikacja została udostępniona publicznie przy użyciu **ngrok**, który tuneluje ruch do lokalnego środowiska Docker Compose. Przygotowano również konfiguracje **Kubernetes** (katalog `k8s/`) gotowe do wdrożenia na platformach chmurowych.

Testy wydajnościowe przeprowadzono przy użyciu **loader.io** — 100 klientów przez 1 minutę.

#### Wyniki testów (loader.io)

| Metryka | FastAPI | Flask |
|---------|---------|-------|
| Średni czas odpowiedzi | 149 ms | 151 ms |
| Min / Max | 147 / 180 ms | 148 / 227 ms |
| Liczba sukcesów | 100 | 100 |
| Błędy 400/500 | 0 / 0 | 0 / 0 |
| Timeout | 0 | 0 |
| Współczynnik błędów | 0.0% | 0.0% |
| Wysłano | 13.96 KB | 13.77 KB |
| Odebrano | 15.33 KB | 15.43 KB |

Obie aplikacje osiągnęły bardzo zbliżone wyniki — brak błędów, stabilny czas odpowiedzi. FastAPI wykazał nieznacznie niższy maksymalny czas odpowiedzi (180 ms vs 227 ms), co świadczy o bardziej stabilnym działaniu pod obciążeniem.

Zrzuty ekranu z testów znajdują się w katalogu `docs/`.

### Zadanie 4 — Ochrona przed botami

W obu aplikacjach, we wszystkich formularzach (sync i async), zaimplementowano trzy mechanizmy ochrony:

#### 1. Pole pułapka (Honeypot)
Ukryte pole `website` niewidoczne dla prawdziwych użytkowników, ale wypełniane automatycznie przez boty. Każde zgłoszenie z wypełnionym tym polem jest natychmiast odrzucane.

```html
<input type="text" name="website" style="display:none">
```

#### 2. Google reCAPTCHA v2
Widżet CAPTCHA wymagający interakcji człowieka przed wysłaniem formularza. Token jest weryfikowany po stronie serwera przez API Google przy użyciu klucza tajnego ze zmiennej środowiskowej `RECAPTCHA_SECRET`.

#### 3. FingerprintJS
Fingerprinting przeglądarki przy użyciu biblioteki open-source [FingerprintJS v4](https://github.com/fingerprintjs/fingerprintjs). Unikalny `visitorId` jest generowany po stronie klienta i przesyłany wraz z formularzem. Backend śledzi liczbę zgłoszeń per urządzenie w tabeli `fingerprint_attempts` i blokuje po przekroczeniu 5 zgłoszeń.

```python
def check_fingerprint(fingerprint: str) -> bool:
    count = run_query(
        "SELECT COUNT(*) FROM fingerprint_attempts WHERE fingerprint=%s",
        (fingerprint,), fetch=True
    )
    if count and count[0][0] >= 5:
        return False
    run_query(
        "INSERT INTO fingerprint_attempts (fingerprint) VALUES (%s)",
        (fingerprint,)
    )
    return True
```

## Uruchomienie lokalne

### Wymagania
- Docker
- Docker Compose

### Zmienne środowiskowe
```bash
cp .env.example .env
# uzupełnij wartości w .env
```

`.env.example`:
```
RECAPTCHA_SECRET=
RECAPTCHA_SITE_KEY=
```

### Uruchamianie
```bash
docker compose up --build
```

Inicjalizacja bazy danych:
```bash
docker exec -i whitefly_1-db-1 psql -U ivansmirnov -d recruitment_tasks_whitefly < schema.sql
```

> **Uwaga:** Nazwa kontenera może się różnić w zależności od nazwy katalogu projektu. Aby sprawdzić poprawną nazwę uruchom:
> ```bash
> docker ps
> ```
> i znajdź kontener z `db` w nazwie.

### Dostęp do aplikacji

| URL | Opis |
|-----|------|
| http://localhost/flask/ | Flask Hello World |
| http://localhost/flask/form_sync | Flask formularz synchroniczny |
| http://localhost/flask/form_async | Flask formularz asynchroniczny |
| http://localhost/fastapi/ | FastAPI Hello World |
| http://localhost/fastapi/form_sync | FastAPI formularz synchroniczny |
| http://localhost/fastapi/form_async | FastAPI formularz asynchroniczny |

## Schemat bazy danych

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    fingerprint_js VARCHAR(255)
);

CREATE TABLE fingerprint_attempts (
    id SERIAL PRIMARY KEY,
    fingerprint VARCHAR(255) NOT NULL,
    attempted_at TIMESTAMP DEFAULT NOW()
);
```

## Stos technologiczny

| Technologia | Zastosowanie |
|-------------|-------------|
| Flask + uWSGI | Aplikacja webowa (Zadanie 1) |
| FastAPI + Uvicorn | Aplikacja webowa (Zadanie 2) |
| Nginx | Rewersowe proxy |
| PostgreSQL | Baza danych |
| Redis | Broker wiadomości |
| Celery | Kolejka zadań asynchronicznych |
| FingerprintJS v4 | Fingerprinting przeglądarki |
| Google reCAPTCHA v2 | Weryfikacja CAPTCHA |
| Docker Compose | Orkiestracja lokalna |
| ngrok | Publiczny dostęp do lokalnego środowiska |
| Kubernetes | Przygotowane konfiguracje wdrożeniowe |
