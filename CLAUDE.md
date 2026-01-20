# CLAUDE.md - POC Application data.gouv

## Contexte projet

POC d'assistant IA pour répondre en langage naturel sur les données publiques françaises.

**Architecture** :
```
Question utilisateur → Embedding BGE-M3 (Albert API)
    → Recherche vectorielle Mediatech → dataset_id
    → MCP datagouv → données fraîches
    → LLM Albert → réponse + sources
```

**Architecture hybride (recommandée après POC)** :
```
Question utilisateur
    ↓
[Recherche Mediatech] → dataset_id          # Recherche sémantique
    ↓
[MCP search/get_resource_info] → URL CSV    # Découverte via MCP
    ↓
[HTTP direct / pandas] → DataFrame          # Téléchargement direct
    ↓
[LLM] → analyse données + réponse           # Analyse avec contexte complet
```

⚠️ **Limitation MCP découverte** : `query_resource_data` et `download_and_parse_resource`
retournent seulement ~3 lignes d'exemple, quel que soit le `page_size` demandé.

## Stack technique

- **Python** : notebooks Jupyter (pas de TypeScript pour ce projet)
- **DuckDB** : requêtes SQL sur Parquet
- **httpx** : appels API (Albert, MCP)
- **Parquet** : catalogue Mediatech (~99k datasets, embeddings BGE-M3 1024 dim)

## Ressources externes

- Mediatech : `AgentPublic/data-gouv-datasets-catalog` sur HuggingFace
- MCP datagouv : `https://mcp.data.gouv.fr/mcp` (Streamable HTTP, JSON-RPC)
- Albert API : endpoint OpenAI-compatible, clé dans `.env`

## Structure projet

```
poc-datagouv/
├── notebooks/          # Développement itératif
│   ├── 01_setup_test.ipynb         # Configuration et tests
│   ├── 02_mediatech_exploration.ipynb  # Exploration données
│   ├── 03_vector_search.ipynb      # Recherche sémantique
│   ├── 04_mcp_client.ipynb         # Client MCP datagouv
│   ├── 05_orchestration.ipynb      # Pipeline complet
│   ├── 06_demo.ipynb               # Interface interactive
│   └── 07_text_to_query.ipynb      # Text-to-query (extraction données)
├── huggingface/        # Parquet Mediatech téléchargé
├── data/               # Données locales (gitignore)
└── .env                # ALBERT_API_KEY (gitignore)
```

## Conventions

- **Code commenté en français**
- **Validation étape par étape** : chaque cellule doit fonctionner avant de passer à la suivante
- **Notebooks = exploration**, `src/` = code propre extrait des notebooks
- Commits : emoji + description concise

## Commandes utiles

```bash
# Activer l'environnement
source .venv/bin/activate

# Lancer Jupyter
jupyter lab

# Tester les imports
python -c "import duckdb, httpx, pandas; print('OK')"
```

## Variables d'environnement

```
ALBERT_API_KEY=xxx          # Requis
ALBERT_API_URL=https://albert.api.etalab.gouv.fr  # Par défaut
```

## Notes techniques

### Mediatech
- Colonne embeddings : `embeddings_bge-m3` (vecteurs 1024 dim, FLOAT[])
- Granularité : chunks (plusieurs par dataset), `doc_id` = identifiant dataset unique
- ~280k chunks pour ~99k datasets

### Albert API
- **Embeddings** : `BAAI/bge-m3` → vecteur 1024 dim
- **LLM** : `mistralai/Mistral-Small-3.2-24B-Instruct-2506` (alias: albert-large)
- Endpoint : `/v1/embeddings`, `/v1/chat/completions` (OpenAI-compatible)

### MCP datagouv
- Transport : Streamable HTTP (POST JSON-RPC)
- Headers requis : `Accept: application/json, text/event-stream`, `http2=False`
- Session : Header `Mcp-Session-Id` retourné après `initialize`
- Réponses en SSE (Server-Sent Events), texte formaté (pas JSON structuré)

**Tools disponibles** :
| Tool | Usage | Status |
|------|-------|--------|
| `search_datasets` | Recherche par mots-clés | ✅ OK |
| `get_dataset_info` | Métadonnées dataset | ✅ OK |
| `list_dataset_resources` | Liste des fichiers | ✅ OK |
| `get_resource_info` | URL + schéma ressource | ✅ OK |
| `get_metrics` | Stats d'usage | ✅ OK |
| `query_resource_data` | Extraction données | ⚠️ Limité à 3 lignes |
| `download_and_parse_resource` | Téléchargement + parsing | ⚠️ Limité à 3 lignes |

**Limitation connue** : Les tools d'extraction de données retournent toujours
"Sample data (first 3 rows)" dans la réponse texte, indépendamment du `page_size`.
→ Workaround : récupérer l'URL via `get_resource_info` puis télécharger directement.

### Text-to-Query (notebook 07)
- **Objectif** : Passer de "trouver le bon dataset" à "extraire les données pertinentes"
- **Paramètres `query_resource_data`** :
  - `resource_id` (requis) : ID de la ressource
  - `question` (requis) : Question en langage naturel (⚠️ informatif seulement, ne filtre pas)
  - `page`, `page_size` : Pagination (mais réponse texte limitée à 3 lignes)
- **Conclusion** : Le paramètre `question` ne filtre pas les données côté serveur.
  L'API retourne toujours les mêmes données brutes paginées.
- **Solution retenue** : Architecture hybride (MCP pour découverte, HTTP pour données)

## Roadmap

1. ✅ Setup environnement
2. ✅ Exploration Mediatech (99k datasets, 40 colonnes)
3. ✅ Recherche vectorielle (Albert embeddings + cosine similarity)
4. ✅ Client MCP datagouv (JSON-RPC sur SSE)
5. ✅ Orchestration LLM (pipeline question → réponse)
6. ✅ Interface interactive (ipywidgets)
7. ✅ Text-to-Query (exploration + architecture hybride documentée)

## Utilisation

```bash
# Lancer la démo
source .venv/bin/activate
jupyter lab
# Ouvrir notebooks/06_demo.ipynb et exécuter toutes les cellules
```

## Conclusions POC

**Ce qui fonctionne bien** :
- Recherche sémantique Mediatech (99k datasets, ~135ms/requête)
- MCP pour la découverte (search, metadata, URLs)
- Pipeline RAG avec Albert LLM
- Interface interactive ipywidgets

**Limitation identifiée** :
- MCP `query_resource_data` retourne seulement 3 lignes d'exemple
- Question en attente auprès du mainteneur MCP data.gouv

**Architecture recommandée** :
```
MCP (découverte) + HTTP direct (données) + LLM (analyse)
```

## Prochaines étapes

1. ⏳ Attendre retour du mainteneur MCP sur la limitation des 3 lignes
2. 📦 Extraire le code des notebooks vers `src/` si le POC évolue en projet
3. 🔄 Tester avec d'autres datasets (différents formats, tailles)
4. 🎨 Améliorer l'interface (Streamlit ou Gradio pour une vraie démo)
