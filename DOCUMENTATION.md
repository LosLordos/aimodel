# HockeyMatch AI - Predikční systém Tipsport Extraligy

Tento projekt je komplexní systém využívající strojové učení (AI) k analýze a predikci výsledků hokejových zápasů české Tipsport Extraligy.

---

## 1. Use Case (Případy užití)

Tento projekt slouží k několika hlavním účelům:
*   **Analytický nástroj pro fanoušky**: Poskytuje objektivní pohled na sílu týmů založený na datech, nikoliv na emocích.
*   **Predikce výsledků**: Odhaduje pravděpodobného vítěze a nejpravděpodobnější skóre zápasu.
*   **Automatizace dat**: Ukazuje, jak automaticky sbírat sportovní výsledky z webu a transformovat je do užitečných statistik (forma, H2H).
*   **Demonstrace AI**: Slouží jako ukázka kompletního cyklu strojového učení (Sběr -> Zpracování -> Učení -> Aplikace).

---

## 2. Jak projekt funguje (Architektura)

Celý systém je rozdělen do čtyř logických fází, které na sebe navazují:

### Fáze A: Sběr dat (`crawler.py`)
*   Program se připojí na hokejové portály a stáhne surové výsledky zápasů (kdo, s kým, kdy a kolik).
*   Výsledkem je základní databáze zápasů.

### Fáze B: Inženýrství příznaků (`dataset_builder.py`)
*   Surová data (např. 3:2) se změní na chytré statistiky.
*   Vypočítá se **forma** (úspěšnost v posledních 10 zápasech), **historická bilance (H2H)** a **střelecká potence** obou týmů v daný moment.

### Fáze C: Trénování mozku (`preprocess.py` & `train_model.py`)
*   Data se převedou do číselné podoby, které rozumí počítač.
*   Model **Gradient Boosting** se "učí" z tisíců odehraných zápasů a hledá v nich vzorce, které vedou k výhře.
*   Výsledné "znalosti" se uloží do souborů ve složce `models/`.

### Fáze D: Predikce a Web (`predict.py` & `app.py`)
*   Webová aplikace přijme od uživatele dva týmy.
*   `predict.py` vytáhne jejich aktuální formu, pošle ji do modelu a ten vrátí procentuální šanci na výhru.

---

## 0. Význam modelových souborů (složka `models/`)

Tyto soubory představují "znalosti" systému, které se vytvořily během trénování. Bez nich by aplikace nevěděla, jak predikovat.

*   **`hockey_model.pkl`**: 
    *   Toto je samotný **natrénovaný mozek** (Gradient Boosting model). 
    *   Obsahuje matematickou strukturu stovek rozhodovacích stromů, které se naučily vztahy mezi statistikami a výsledky zápasů.
*   **`team_encoder.pkl`**: 
    *   Funguje jako **překladový slovník**. 
    *   Uchovává informaci o tom, že např. "HC Sparta Praha" odpovídá číslu `12`. Je kriticky důležité, aby se při predikci používala stejná čísla jako při tréninku.
*   **`feature_names.pkl`**: 
    *   Seznam **názvů sloupců** v přesném pořadí. 
    *   Zajišťuje, že statistiky (forma, H2H atd.) posíláme do modelu ve správném pořadí. Pokud bychom je prohodili, model by podával nesmyslné výsledky.

---

## 1 Proč používáme Gradient Boosting (a ne Random Forest)?

V projektu je použit **GradientBoostingClassifier**. I když oba modely používají "rozhodovací stromy", Gradient Boosting je pro tento úkol vhodnější:

1.  **Sekvenční učení**: Random Forest staví stromy nezávisle. Gradient Boosting staví stromy jeden po druhém, přičemž každý nový strom se snaží opravit chyby těch předchozích. Pro komplexní sportovní data to bývá přesnější.
2.  **Optimalizace**: Gradient Boosting je citlivější na parametry (jako je `learning_rate`), což nám umožnilo model lépe "vyladit" na přesnost přes 60 %.
3.  **Váha příznaků**: Tento model lépe identifikuje klíčové statistiky (např. že vzájemné zápasy mají větší váhu než samotný název týmu).

---


## 2. Predikce vítěze (predict.py -> predict_winner)

Metoda `predict_winner` kombinuje statistickou historii s modelem strojového učení.

1.  **Načtení stavu**: Získá nejaktuálnější řádek statistik pro oba týmy z `matches_featured.csv`.
2.  **Kódování**: Převede názvy týmů na čísla pomocí uloženého `team_encoder.pkl`.
3.  **Vstupní vektor**: Vytvoří se řádek dat, který obsahuje:
    *   ID týmů, formy, průměry gólů, H2H a brankové rozdíly.
4.  **Model Inference**: 
    *   `model.predict()`: Vrátí 1 (tým A vyhraje) nebo 0 (tým B vyhraje).
    *   `model.predict_proba()`: Vrátí pravděpodobnost pro obě varianty (např. `[0.4, 0.6]`). Ta se používá pro zobrazení **Confidence (Důvěry)** v aplikaci.

---

## 3. Algoritmus odhadu skóre (predict.py -> predict_score)

Odhad skóre není dělán modelem ML (ten by byl méně přesný), ale pomocí **heuristického výpočtu**:

```python
# Logika výpočtu pro tým A
očekávané_góly_A = (průměr_vstřelených_A + průměr_inkasovaných_B) / 2
skóre_A = očekávané_góly_A * (forma_A + 0.5)
```

### Proč tato logika?
*   **Kombinace útoku a obrany**: Pokud tým A střílí hodně gólů, ale tým B má skvělou obranu, výsledek bude někde uprostřed.
*   **Vliv formy**: Člen `(forma_A + 0.5)` funguje jako násobič. 
    *   Pokud má tým perfektní formu (1.0), jeho očekávaný počet gólů se násobí `1.5`. 
    *   Pokud má tragickou formu (0.0), násobí se jen `0.5`.
*   **Zaokrouhlování**: Výsledek se zaokrouhluje na celá čísla, aby vypadal jako reálný hokejový výsledek.

---

## 4. Detailní rozbor kódu train_model.py

Tento skript je "učitelem" celého systému. Bere připravená data a vytváří z nich predikční model. Zde je kompletní kód a jeho vysvětlení:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import os
from preprocess import preprocess_data

def train():
    print("Loading and preprocessing data...")
    # Načtení dat pomocí dříve vysvětleného skriptu preprocess.py
    X, y, feature_names = preprocess_data("data/matches_featured.csv")
    
    # Rozdělení dat na trénovací a testovací sadu (80% trénink, 20% test)
    # random_state=42 zajišťuje, že při každém spuštění bude rozdělení stejné
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training model on {len(X_train)} samples with {len(feature_names)} features...")
    
    # Konfigurace algoritmu Gradient Boosting
    model = GradientBoostingClassifier(
        n_estimators=300,    # Počet stromů v lese (víc stromů = detailnější model)
        learning_rate=0.03,  # Jak moc se model učí z chyb každého stromu
        max_depth=4,         # Jak složité/hluboké mohou být stromy (prevence přetrénování)
        subsample=0.8,       # Model se učí na náhodných 80% dat (zvyšuje odolnost)
        random_state=42
    )
    # Samotný proces učení
    model.fit(X_train, y_train)
    
    # Testování modelu na datech, která model nikdy neviděl (X_test)
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    cm = confusion_matrix(y_test, predictions)
    
    # Výpis výsledků
    print("\n--- Model Evaluation ---")
    print(f"Accuracy: {acc:.4f}")
    
    # Analýza důležitosti statistik
    print("\n--- Feature Importance ---")
    importances = model.feature_importances_
    for name, importance in zip(feature_names, importances):
        print(f"{name}: {importance:.4f}")
        
    print("\nConfusion Matrix:")
    print(cm) # Tabulka ukazující, kolikrát se model trefil a kolikrát se spletl
    
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    # Uložení finálního "mozku" do souboru
    if not os.path.exists('models'): os.makedirs('models')
    joblib.dump(model, 'models/hockey_model.pkl')
    # Uložení názvů sloupců pro zajištění konzistence při predikci
    joblib.dump(feature_names, 'models/feature_names.pkl')
    print("\nModel saved to models/hockey_model.pkl")
```

### Rozbor klíčových částí:

1.  **`train_test_split`**: Je kriticky důležité model testovat na jiných datech, než na kterých se učil. Pokud by se učil i testoval na stejných datech, "nabifloval" by se je nazpaměť a v reálném světě by nefungoval.
2.  **`GradientBoostingClassifier`**: Tento model funguje tak, že postupně přidává stromy, kde každý nový strom opravuje chyby těch předchozích. Je to jeden z nejvýkonnějších nástrojů pro hokejové statistiky.
3.  **`feature_importances_`**: Ukazuje nám, co model považuje za důležité. Pokud by například `h2h_winner_a` mělo hodnotu 0.20, znamená to, že vzájemné zápasy mají 20% vliv na finální rozhodnutí modelu.
4.  **`confusion_matrix`**: Matice záměn. Ukazuje:
    *   Kolikrát model správně určil výhru.
    *   Kolikrát model správně určil prohru.
    *   Kolikrát se spletl a zaměnil výhru za prohru.
5.  **`joblib.dump`**: Převede objekt modelu z operační paměti na disk. Díky tomu webová aplikace (`app.py`) nemusí nic trénovat, ale jen načte hotový výsledek.

---

## 5. Detailní rozbor kódu predict.py

Tento skript je srdcem aplikace pro uživatele. Zde je kompletní kód a jeho vysvětlení:

```python
import joblib
import pandas as pd
import numpy as np
import os

class HockeyPredictor:
    def __init__(self):
        # Inicializace: Načtení natrénovaného modelu a pomocných souborů
## 5. Podrobný rozbor kódu predict.py (Srdce aplikace)

Tento skript zajišťuje načtení modelu a výpočet predikcí. Zde je vysvětlení logiky řádek po řádku:

### 1. Importy a Inicializace (Metoda `__init__`)
*   **Knihovny**: Používáme `joblib` pro načtení natrénovaného "mozku" a `pandas` pro práci s databází zápasů.
*   **Načítání znalostí**: V konstruktoru se načítají tři klíčové soubory z trénování:
    *   `hockey_model.pkl`: Samotná umělá inteligence (Gradient Boosting).
    *   `team_encoder.pkl`: Převodník, který ví, že např. "Sparta" odpovídá číslu 12.
    *   `feature_names.pkl`: Seznam statistik v přesném pořadí, které model očekává.
*   **Databáze**: Načítáme `matches1.csv`, abychom mohli v reálném čase zjišťovat aktuální formu týmů.

### 2. Metoda `get_latest_stats` (Hledání formy)
*   Tato funkce funguje jako "paměť". Podívá se do historie a najde úplně poslední odehraný zápas daného týmu.
*   Zjistí, zda tým hrál doma nebo venku, a vytáhne jeho aktuální parametry:
    *   **Forma**: Úspěšnost v posledních 10 zápasech.
    *   **Avg Scored/Conceded**: Průměrný počet gólů, které tým dává a dostává.
*   Tyto hodnoty jsou klíčovým vstupem pro dnešní predikci.

### 3. Metoda `get_h2h_stat` (Vzájemná historie)
*   Hledá všechny zápasy, kde se tito dva soupeři potkali v minulosti (Head-to-Head).
*   Vypočítá úspěšnost (Win Rate): Výhra = 1, Remíza = 0.5, Prohra = 0.
*   Výsledné číslo (např. 0.7 pro 70% úspěšnost) dává modelu informaci o tom, zda má jeden tým na druhého "recept".

### 4. Metoda `predict_score` (Odhad skóre)
*   Zde se nepoužívá AI, ale logický výpočet (heuristika).
*   Bere se průměr mezi útokem týmu A a obranou týmu B (a naopak).
*   Výsledek se vynásobí koeficientem formy. Pokud je tým "rozjetý", jeho odhadovaný počet gólů se zvýší.

### 5. Metoda `predict_winner` (Rozhodnutí AI)
*   Toto je hlavní řídící centrum. Sesbírá data od všech ostatních metod.
*   **Kódování**: Převede textová jména týmů na čísla, kterým model rozumí.
*   **Predict Proba**: Model analyzuje všech 11 vstupních parametrů a vrátí pravděpodobnost výhry pro oba týmy.
*   Vše se zabalí do výsledného balíčku (JSON), který webová aplikace zobrazí uživateli.

---

```python
    def get_latest_stats(self, team_name):
        # Vyhledá poslední zápas týmu a vrátí jeho aktuální statistiky
        team_matches = self.df_featured[
            (self.df_featured['team_a'] == team_name) | 
            (self.df_featured['team_b'] == team_name)
        ].sort_values('date', ascending=False)
        if team_matches.empty: return None
        
        latest = team_matches.iloc[0]
        # Pokud byl tým v posledním zápase jako team_a, vezmeme staty '_a', jinak '_b'
        if latest['team_a'] == team_name:
            return {
                'form': latest['form_a'],
                'avg_scored': latest['avg_goals_scored_a'],
                'avg_conceded': latest['avg_goals_conceded_a'],
                'gd_form': latest['gd_form_a']
            }
        else:
            return {
                'form': latest['form_b'],
                'avg_scored': latest['avg_goals_scored_b'],
                'avg_conceded': latest['avg_goals_conceded_b'],
                'gd_form': latest['gd_form_b']
            }

    def get_h2h_stat(self, team_a, team_b):
        # Filtrace všech vzájemných zápasů v historii
        h2h = self.df_featured[
            ((self.df_featured['team_a'] == team_a) & (self.df_featured['team_b'] == team_b)) |
            ((self.df_featured['team_a'] == team_b) & (self.df_featured['team_b'] == team_a))
        ]
        if h2h.empty: return 0.5, 0, []
        
        results = []
        h2h_list = []
        for _, match in h2h.iterrows():
            # Výpočet úspěšnosti z pohledu team_a
            if match['team_a'] == team_a:
                res = 1 if match['goals_a'] > match['goals_b'] else (0.5 if match['goals_a'] == match['goals_b'] else 0)
            else:
                res = 1 if match['goals_b'] > match['goals_a'] else (0.5 if match['goals_b'] == match['goals_a'] else 0)
            
            results.append(res)
            h2h_list.append({
                "date": str(match['date']),
                "team_a": match['team_a'],
                "team_b": match['team_b'],
                "score": f"{match['goals_a']}:{match['goals_b']}"
            })
        return np.mean(results), len(h2h), h2h_list

    def predict_score(self, stats_a, stats_b):
        # Heuristika pro odhad skóre
        score_a = (stats_a['avg_scored'] + stats_b['avg_conceded']) / 2
        score_b = (stats_b['avg_scored'] + stats_a['avg_conceded']) / 2
        # Úprava podle formy
        score_a *= (stats_a['form'] + 0.5)
        score_b *= (stats_b['form'] + 0.5)
        return round(score_a), round(score_b)

    def predict_winner(self, team_a, team_b):
        # Hlavní metoda pro celkovou predikci
        try:
            # Převod jmen na čísla (např. 'Sparta' -> 12)
            team_a_enc = self.encoder.transform([team_a])[0]
            team_b_enc = self.encoder.transform([team_b])[0]
        except ValueError:
            return "Error: Team not found."

        stats_a = self.get_latest_stats(team_a)
        stats_b = self.get_latest_stats(team_b)
        h2h_a, h2h_count, h2h_matches = self.get_h2h_stat(team_a, team_b)

        # Vytvoření tabulky pro model (musí mít stejné sloupce jako při tréninku)
        input_data = pd.DataFrame([{
            'team_a_encoded': team_a_enc, 'team_b_encoded': team_b_enc,
            'form_a': stats_a['form'], 'form_b': stats_b['form'],
            'avg_goals_scored_a': stats_a['avg_scored'], 'avg_goals_conceded_a': stats_a['avg_conceded'],
            'avg_goals_scored_b': stats_b['avg_scored'], 'avg_goals_conceded_b': stats_b['avg_conceded'],
            'gd_form_a': stats_a['gd_form'], 'gd_form_b': stats_b['gd_form'],
            'h2h_winner_a': h2h_a
        }])

        input_data = input_data[self.feature_names]
        prob = self.model.predict_proba(input_data)[0]
        prediction = self.model.predict(input_data)[0]
        
        winner = team_a if prediction == 1 else team_b
        confidence = prob[1] if prediction == 1 else prob[0]
        pred_goals_a, pred_goals_b = self.predict_score(stats_a, stats_b)
        
        return {
            "winner": winner, "confidence": f"{confidence*100:.2f}%",
            "team_a": team_a, "team_b": team_b,
            "h2h_win_rate": f"{h2h_a*100:.1f}%",
            "h2h_matches": h2h_matches[:10],
            "predicted_score": f"{pred_goals_a}:{pred_goals_b}",
            "stats_a": stats_a, "stats_b": stats_b
        }
```

---

## 1.1 Detailní vzorce a výpočty metrik

V této sekci jsou vysvětleny přesné výpočty, které se v aplikaci používají pro zhodnocení síly týmů.

### 1. Jak se počítá **Forma**?
Forma týmu vyjadřuje jeho úspěšnost v posledních **10 odehraných zápasech**.
*   **Bodování pro výpočet**: Výhra = 1 bod, Remíza/Prodloužení = 0.5 bodu, Prohra = 0 bodů.
*   **Kód pro výpočet**:
    ```python
    # Body z pohledu týmu
    points = 1 if team_won else (0.5 if draw else 0)
    # Klouzavý průměr z posledních 10 zápasů
    df['form'] = df['points'].rolling(window=10).mean().shift(1)
    ```
*   Tato hodnota se pohybuje od **0.0 (nejhorší)** do **1.0 (nejlepší)**.

### 2. Jak se počítá **Úspěšnost (H2H)**?
Tato hodnota ukazuje historickou dominanci jednoho týmu nad druhým.
*   **Kód pro výpočet** (z `predict.py`):
    ```python
    # Procházíme vzájemné zápasy a sčítáme úspěšnost týmu A
    for _, match in h2h.iterrows():
        if match['team_a'] == team_a:
            res = 1 if match['goals_a'] > match['goals_b'] else (0.5 if match['goals_a'] == match['goals_b'] else 0)
        else:
            res = 1 if match['goals_b'] > match['goals_a'] else (0.5 if match['goals_b'] == match['goals_a'] else 0)
        results.append(res)
    # Finální procento je průměr těchto výsledků
    h2h_win_rate = np.mean(results)
    ```

### 3. Jak se počítá **Průměr vstřelených a inkasovaných gólů**?
Vypočítává se jako klouzavý průměr z posledních **10 zápasů** daného týmu.
*   **Kód pro výpočet**:
    ```python
    # Průměr gólů vstřelených týmem v posledních 10 zápasech
    df['avg_scored'] = df['goals_scored'].rolling(window=10).mean().shift(1)
    # Průměr gólů inkasovaných týmem v posledních 10 zápasech
    df['avg_conceded'] = df['goals_conceded'].rolling(window=10).mean().shift(1)
    ```

### 4. Jak se počítá **Procento na výhru (Confidence)**?
Toto procento je výsledek **Gradient Boosting algoritmu**.
*   **Kód pro výpočet**:
    ```python
    # Model analyzuje všech 11 příznaků a vrátí pravděpodobnosti pro obě strany
    prob = self.model.predict_proba(input_data)[0] # Vrací [šance_na_0, šance_na_1]
    
    # Pokud model predikuje 1 (výhra týmu A), vezmeme druhou hodnotu
    confidence = prob[1] if prediction == 1 else prob[0]
    ```

---
```

### Rozbor klíčových částí:

1.  **`__init__`**: Tato metoda se spustí jednou při startu aplikace. Načte "mozek" (model) a "paměť" (seznam týmů a historii zápasů). Bez těchto souborů by aplikace nevěděla, co má dělat.
2.  **`get_latest_stats`**: Funguje jako vyhledávač. Podívá se do souboru `matches1.csv` a najde poslední známý stav týmu. Pokud tým hrál naposledy včera a vyhrál 5:0, jeho forma bude vysoká a tyto hodnoty se použijí pro dnešní predikci.
3.  **`get_h2h_stat`**: Tato metoda prochází celou historii. Pokud Sparta a Třinec spolu hráli 20x, spočítá, kolikrát vyhrála Sparta. Tento poměr (`h2h_win_rate`) je pro model jeden z nejdůležitějších údajů.
4.  **`predict_score`**: Zde nepoužíváme umělou inteligenci, ale logický vzorec. Bere se průměr gólů týmu A a gólů, které dostává tým B. Pokud Sparta dává 4 góly a Třinec jich dostává 2, odhad bude někde kolem 3 gólů. To se pak násobí koeficientem formy.
5.  **`predict_winner`**: Toto je "řídící věž". 
    *   Sesbírá data od všech ostatních metod.
    *   Zformátuje je do podoby, kterou model očekává.
    *   **`model.predict_proba`**: Neříká jen kdo vyhraje, ale jak moc si je model jistý (např. 0.8 vs 0.2).
    *   Vše zabalí do přehledného balíčku (slovníku), který webová stránka snadno zobrazí.

---

## 6. Webová aplikace (app.py & templates)

*   **Flask (Backend)**: Funguje jako most. Přijme požadavek z webu, zavolá Python metody a pošle odpověď zpět jako JSON.
*   **Frontend (index.html)**: 
    *   Používá **asynchronní JavaScript (fetch)**, takže se stránka při predikci nemusí obnovovat.
    *   Dynamicky generuje tabulku vzájemných zápasů ze seznamu, který pošle `predict.py`.
