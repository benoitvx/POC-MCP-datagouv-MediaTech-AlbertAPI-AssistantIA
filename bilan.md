# Bilan POC - Assistant IA data.gouv.fr

**Date** : Janvier 2025
**Durée** : ~1 journée
**Objectif** : Valider la faisabilité d'un assistant IA capable de répondre en langage naturel sur les données publiques françaises

---

## Résumé exécutif

Le POC démontre qu'il est **techniquement faisable** de construire un assistant IA interrogeant data.gouv.fr en langage naturel. L'architecture combine recherche sémantique (Mediatech), découverte de données (MCP) et génération de réponses (Albert LLM).

**Verdict** : ✅ Faisable avec une architecture hybride

---

## Composants testés

### 1. Mediatech (HuggingFace)
| Aspect | Résultat |
|--------|----------|
| Données | 99 245 datasets pré-vectorisés |
| Embeddings | BGE-M3, 1024 dimensions |
| Format | Parquet (~400 MB en mémoire) |
| Performance | ~135ms par recherche |
| Qualité | Bonne pertinence sémantique |

**Verdict** : ✅ Excellent pour la recherche de datasets

### 2. Albert API (Etalab)
| Aspect | Résultat |
|--------|----------|
| Embeddings | `BAAI/bge-m3` - fonctionne bien |
| LLM | `mistralai/Mistral-Small-3.2-24B-Instruct-2506` |
| Latence | ~2-3s pour une réponse |
| Qualité | Réponses pertinentes en français |
| API | Compatible OpenAI |

**Verdict** : ✅ Production-ready

### 3. MCP data.gouv.fr
| Tool | Status | Notes |
|------|--------|-------|
| `search_datasets` | ✅ | Recherche par mots-clés |
| `get_dataset_info` | ✅ | Métadonnées complètes |
| `list_dataset_resources` | ✅ | Liste des fichiers |
| `get_resource_info` | ✅ | URL directe + schéma |
| `get_metrics` | ✅ | Stats d'usage |
| `query_resource_data` | ⚠️ | Limité à 3 lignes |
| `download_and_parse_resource` | ⚠️ | Limité à 3 lignes |

**Verdict** : ⚠️ Utile pour la découverte, limité pour l'extraction de données

---

## Architecture validée

```
┌─────────────────────────────────────────────────────────────┐
│                    Question utilisateur                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. RECHERCHE SÉMANTIQUE (Mediatech)                        │
│     - Embedding de la question (Albert BGE-M3)              │
│     - Similarité cosinus sur 99k datasets                   │
│     - Retourne top-k datasets pertinents                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. DÉCOUVERTE (MCP data.gouv)                              │
│     - get_resource_info → URL du CSV/JSON                   │
│     - Récupère le schéma des colonnes                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. TÉLÉCHARGEMENT (HTTP direct)                            │
│     - pandas.read_csv() sur l'URL                           │
│     - Données complètes en DataFrame                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. ANALYSE (Albert LLM)                                    │
│     - Contexte : échantillon des données + question         │
│     - Génère une réponse avec chiffres concrets             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Réponse + Sources citées                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Limitation majeure identifiée

### MCP : Extraction de données limitée

**Constat** : Les tools `query_resource_data` et `download_and_parse_resource` retournent toujours 3 lignes d'exemple maximum dans leur réponse texte, quel que soit le `page_size` demandé.

**Exemple** :
```
Retrieved: 100 row(s) from page 1
...
Sample data (first 3 rows):
  Row 1: ...
  Row 2: ...
  Row 3: ...
  ... (97 more row(s) available)
```

**Impact** : Le LLM ne peut analyser que 3 lignes, insuffisant pour des statistiques fiables.

**Workaround** : Télécharger le CSV directement via l'URL fournie par `get_resource_info`.

**Status** : Question posée au mainteneur MCP data.gouv.

---

## Notebooks produits

| Notebook | Contenu | Status |
|----------|---------|--------|
| `01_setup_test.ipynb` | Configuration environnement | ✅ |
| `02_mediatech_exploration.ipynb` | Exploration des 99k datasets | ✅ |
| `03_vector_search.ipynb` | Recherche sémantique Albert | ✅ |
| `04_mcp_client.ipynb` | Client MCP JSON-RPC/SSE | ✅ |
| `05_orchestration.ipynb` | Pipeline RAG complet | ✅ |
| `06_demo.ipynb` | Interface ipywidgets | ✅ |
| `07_text_to_query.ipynb` | Extraction données + analyse | ✅ |

---

## Métriques de performance

| Opération | Temps |
|-----------|-------|
| Chargement Mediatech (99k embeddings) | ~10s |
| Embedding d'une question | ~80ms |
| Recherche vectorielle (99k datasets) | ~50ms |
| Appel MCP (search_datasets) | ~500ms |
| Génération réponse LLM | ~2-3s |
| **Pipeline complet** | **~4-5s** |

---

## Points forts

1. **Stack 100% souveraine** : Albert API (Etalab) + données publiques françaises
2. **Recherche sémantique efficace** : BGE-M3 multilingue, bonne qualité
3. **Catalogue riche** : 99k datasets pré-indexés via Mediatech
4. **API standard** : MCP et Albert sont bien documentés
5. **Prototype rapide** : 7 notebooks en ~1 journée

---

## Points d'amélioration

1. **MCP limité** : Extraction données plafonnée à 3 lignes
2. **Contexte LLM** : Datasets volumineux dépassent la fenêtre de contexte
3. **Fraîcheur** : Mediatech peut avoir du retard sur data.gouv.fr live
4. **Interface** : ipywidgets basique, pas production-ready

---

## Recommandations

### Court terme
- [ ] Attendre retour mainteneur MCP sur la limitation des 3 lignes
- [ ] Documenter le workaround HTTP direct

### Moyen terme
- [ ] Migrer vers Streamlit/Gradio pour une vraie interface
- [ ] Implémenter un cache des datasets fréquemment consultés
- [ ] Ajouter des filtres (organisation, date, format)

### Long terme
- [ ] Intégrer un vrai moteur de requêtes (DuckDB sur les CSV téléchargés)
- [ ] Fine-tuner un modèle spécialisé data.gouv.fr
- [ ] Déployer en production (API + frontend)

---

## Conclusion

Le POC valide la faisabilité technique d'un assistant IA sur data.gouv.fr. L'architecture hybride (Mediatech + MCP + HTTP direct + Albert) contourne les limitations actuelles du MCP.

**Prochaine étape** : Clarifier avec l'équipe MCP data.gouv si l'extraction de données complètes est prévue, puis décider de la suite à donner au projet.

---

## Annexes

### Dépendances Python
```
duckdb
httpx
pandas
numpy
python-dotenv
ipywidgets
jupyterlab
```

### Variables d'environnement
```
ALBERT_API_KEY=sk-xxx
ALBERT_API_URL=https://albert.api.etalab.gouv.fr/v1
MCP_DATAGOUV_URL=https://mcp.data.gouv.fr/mcp
```

### Ressources
- Mediatech : https://huggingface.co/datasets/AgentPublic/data-gouv-datasets-catalog
- Albert API : https://albert.api.etalab.gouv.fr
- MCP data.gouv : https://mcp.data.gouv.fr
