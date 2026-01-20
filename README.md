# POC Application data.gouv

Assistant IA pour interroger les données publiques françaises en langage naturel.

## Stack

- **Mediatech** : catalogue data.gouv pré-vectorisé (99k datasets, embeddings BGE-M3)
- **datagouv-mcp** : serveur MCP pour accès temps réel aux données
- **Albert API** : LLM souverain + embeddings

## Setup

```bash
# Créer et activer l'environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec votre clé Albert API

# Lancer Jupyter
jupyter lab
```

## Structure

```
poc-datagouv/
├── notebooks/          # Notebooks Jupyter
│   ├── 01_setup_test.ipynb
│   ├── 02_mediatech_exploration.ipynb
│   └── ...
├── src/                # Modules Python
├── data/               # Données (Parquet Mediatech)
├── .env.example
└── requirements.txt
```

## Notebooks

1. **01_setup_test** : Vérification de l'installation
2. **02_mediatech_exploration** : Chargement et exploration du catalogue
3. **03_vector_search** : Recherche sémantique avec Albert
4. **04_mcp_client** : Client MCP datagouv
5. **05_orchestration** : Flow complet question → réponse
6. **06_demo** : Interface finale

## Ressources

- [Mediatech (HuggingFace)](https://huggingface.co/datasets/AgentPublic/data-gouv-datasets-catalog)
- [MCP data.gouv.fr](https://mcp.data.gouv.fr/mcp)
