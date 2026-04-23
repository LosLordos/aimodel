# 📘 HockeyMatch AI - Kompletní technická dokumentace

Tento dokument slouží jako hlavní průvodce projektem HockeyMatch AI. Obsahuje vysvětlení architektury, matematických vzorců, logiky strojového učení i návod k obsluze.

---

## 1. Účel projektu (Use Case)
Projekt byl vytvořen s cílem demonstrovat sílu strojového učení v oblasti sportovní analytiky.
*   **Analýza výkonnosti**: Sledování formy týmů české Tipsport Extraligy.
*   **Predikce výsledků**: Odhadování pravděpodobnosti výhry na základě historických dat (sezóny 2023–2025).
*   **Automatizace**: Od sběru dat (scraping) až po webovou vizualizaci bez nutnosti ručního zásahu.

---

## 2. Architektura systému (Workflow)
Projekt se skládá z pěti logických kroků, které tvoří uzavřený cyklus:

1.  **Sběr dat (`crawler.py`)**: Stahování surových výsledků z webu hokej.cz.
2.  **Inženýrství příznaků (`dataset_builder.py`)**: Výpočet pokročilých metrik (forma, H2H, průměry gólů).
3.  **Příprava pro AI (`preprocess.py`)**: Čištění dat a kódování názvů týmů na čísla.
4.  **Trénování modelu (`train_model.py`)**: Vytvoření "mozku" aplikace pomocí algoritmu Gradient Boosting.
5.  **Aplikace (`app.py` & `predict.py`)**: Interaktivní webové rozhraní pro uživatele.

---

## 3. Konfigurace (`config.py`)
Pro snadnou správu projektu používáme centrální konfigurační soubor. Ten umožňuje měnit nastavení (např. port webu nebo cesty k souborům) na jednom místě:
```python
class Config:
    PORT = 5001
    DATA_DIR = 'data'
    MODEL_FILE = 'models/hockey_model.pkl'
    # ... další nastavení
```

---

## 4. Matematické vzorce a výpočty metrik

### 4.1 Výpočet Formy
Forma týmu je klouzavý průměr úspěšnosti z posledních **10 zápasů**.
*   **Výhra** = 1.0 bod
*   **Remíza/Prodloužení** = 0.5 bodu
*   **Prohra** = 0.0 bodů
*   **Vzorec**: `df['form'] = df['points'].rolling(window=10).mean().shift(1)`

### 4.2 Historická úspěšnost (H2H - Head to Head)
Ukazuje, jak se týmu A dařilo proti týmu B v celé historii databáze.
*   Prochází se všechny zápasy, kde se tyto dva týmy potkaly.
*   Vypočítá se průměr bodů týmu A z těchto konkrétních zápasů.

---

## 5. Strojové učení (Gradient Boosting)

### Proč Gradient Boosting?
Používáme **Gradient Boosting Classifier**, protože na rozdíl od Random Forestu staví stromy sekvenčně. Každý nový strom se učí z chyb těch předchozích. To je ideální pro sportovní data, kde jsou vztahy mezi statistikami velmi komplexní.

### Vstupní parametry (Features)
Model se rozhoduje na základě 11 parametrů:
1.  ID Týmu A / ID Týmu B
2.  Aktuální forma obou týmů
3.  Průměr vstřelených gólů (posledních 10 zápasů)
4.  Průměr inkasovaných gólů (posledních 10 zápasů)
5.  Brankový rozdíl ve formě (Goal Difference Form)
6.  Historická úspěšnost H2H

---

## 6. Rozbor predikční logiky (`predict.py`)

Tato třída (`HockeyPredictor`) je mostem mezi uloženým modelem a uživatelem.

*   **`get_latest_stats`**: Vyhledá v databázi nejčerstvější data o týmu před dnešním zápasem.
*   **`predict_score`**: Používá heuristiku (průměry gólů upravené o formu) k odhadu výsledného skóre.
*   **`predict_winner`**: Nejdůležitější metoda. Pošle data do AI modelu a získá pravděpodobnost výhry přes `model.predict_proba()`.

---

## 7. Webové rozhraní (`app.py`)

Aplikace běží na frameworku **Flask**.
*   **Trasa `/`**: Zobrazí hlavní stránku a načte seznam všech dostupných týmů z enkodéru.
*   **Trasa `/predict`**: Přijímá POST požadavky s názvy týmů, zavolá `predict.py` a vrátí výsledek ve formátu JSON.

---

## 8. Význam souborů v `models/`

*   **`hockey_model.pkl`**: Natrénovaný algoritmus (mozek).
*   **`team_encoder.pkl`**: Převodník textu na čísla (např. "HC Sparta Praha" -> 12).
*   **`feature_names.pkl`**: Zajišťuje správné pořadí statistik při vstupu do modelu.

---

## 9. Jak projekt spustit
1.  **Instalace**: `pip install -r requirements.txt`
2.  **Spuštění**: Klikněte na `run.bat` (Windows) nebo `run.sh` (Mac/Linux).
3.  **Prohlížeč**: Otevřete adresu `http://127.0.0.1:5001`.

---
© 2026 HockeyMatch AI Project
