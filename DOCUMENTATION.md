# 📘 HockeyMatch AI - Kompletní technická dokumentace

Tento dokument slouží jako hlavní průvodce projektem HockeyMatch AI. Obsahuje vysvětlení architektury, matematických vzorců, logiky strojového učení i návod k obsluze.

---

## 1. Účel projektu a Use Case (Případy užití)
Projekt byl vytvořen s cílem demonstrovat sílu strojového učení v oblasti sportovní analytiky. Zde jsou konkrétní situace, kde systém najde uplatnění:

*   **Předzápasová analýza pro fanoušky**: Uživatel chce vědět, zda má jeho oblíbený tým šanci proti silnému soupeři na základě historie, a ne jen na základě emocí.
*   **Identifikace "formy"**: Systém odhalí týmy, které mají v posledních zápasech vzestupnou tendenci, i když jsou v tabulce nízko.
*   **Odhad vývoje skóre**: Díky analýze průměrů gólů dokáže systém odhadnout, zda bude zápas defenzivní (málo gólů) nebo ofenzivní.
*   **Vzdělávací účely**: Ukázka toho, jak v reálném světě propojit Web Scraping, Data Science a Web Development do jednoho funkčního celku.

---

## 2. Jak projekt funguje (Workflow & Příklad)
Systém nefunguje jen jako statická databáze, ale jako dynamický proces. Představme si situaci, kdy chcete predikovat zápas **Sparta vs. Pardubice**:

1.  **Sběr dat (`crawler.py`)**: Systém projede web hokej.cz a zjistí, že včera Sparta vyhrála 4:1 a Pardubice prohrály 0:2.
2.  **Výpočet statistik (`dataset_builder.py`)**: Tato nová data se započítají do "Formy". Sparta má teď formu např. 0.8 (vysoká), Pardubice 0.4 (pokles).
3.  **Vstup do AI (`predict.py`)**: Uživatel vybere tyto dva týmy na webu. Skript `predict.py` vytáhne tyto čerstvé statistiky a vytvoří "vstupní lístek" pro model.
4.  **Verdikt modelu (`hockey_model.pkl`)**: Model Gradient Boosting porovná tento lístek s tisíci zápasy, které už zná z minulosti, a vypočítá: *"V 72 % případů s těmito parametry vyhrál domácí tým."*
5.  **Zobrazení výsledku**: Webové rozhraní vám ukáže vítěze, procentuální jistotu a předpokládaný výsledek (např. 3:1).

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
