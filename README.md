# ML Model Deployment API

## Résumé

API REST en FastAPI pour exposer un modèle de machine learning (format joblib).
Le service reçoit un dictionnaire de features, renvoie une prédiction binaire
(0/1) et la probabilité associée. Les requêtes et résultats peuvent être
persistés en base (PostgreSQL) via SQLAlchemy.

## Contexte

Ce dépôt regroupe le code serveur, le modèle entraîné (joblib) et la couche
de persistance. Il a été développé dans le cadre du projet pédagogique
"Déployez votre modèle de Machine Learning".

## Technos principales

- Python 3.10+
- FastAPI (API)
- SQLAlchemy (ORM)
- joblib / scikit-learn (modèle)
- Pytest (tests)
- PostgreSQL (persistance)

## Arborescence clé

```
./
├── app/                 # code de l'application (routes, db, modèles ML)
│   ├── main.py          # point d'entrée FastAPI
│   ├── db/              # session et modèles SQLAlchemy
│   └── ml/              # loader et artefacts du modèle
├── docs/                # documentation/support (ex: db_schema.txt)
├── tests/               # tests unitaires et d'intégration
├── requirements.txt     # dépendances
└── README.md
```

## Installation locale

1. Créez un environnement Python (venv/conda) avec Python 3.10+. Exemple :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Préparez la base de données (PostgreSQL) et configurez la variable
   d'environnement `DATABASE_URL` (format SQLAlchemy). Exemple :

```bash
export DATABASE_URL="postgresql+psycopg2://user:pass@localhost:5432/dbname"
```

3. Créez les tables (si nécessaire) via le script `app/db/create_db.py` ou
   avec vos migrations (Alembic si ajouté).

## Exécution

Lancer le serveur en développement :

```bash
uvicorn app.main:app --reload
```

## Endpoints

1. GET /health

- Description : vérifie que l'API est up.
- Réponse : 200 {"status":"ok"}

2. POST /predict

- Description : envoie un dictionnaire de features et reçoit la prédiction
  et la probabilité.
- Payload (JSON) :

```json
{
	"features": {
		"age": 35,
		"age_debut_carriere": 22,
		"annee_experience_totale": 13,
		... (toutes les features attendues) ...
	}
}
```

- Réponse (200) :

```json
{
  "prediction": 1,
  "probability": 0.78
}
```

## Validation et liste des features attendues

Le serveur valide la présence et la cohérence d'un ensemble de features
attendues (liste complète dans `app/main.py` variable `EXPECTED_FEATURES`).
En cas de feature manquante ou incohérence, l'API renvoie 400 avec le détail
de l'erreur.

## Modèle

Le loader de modèle se trouve dans `app/ml/model.py` et charge
`app/ml/models/model_p4.joblib`. Assurez-vous que ce fichier existe et est
compatible (même jeu de features et ordre). Si le modèle est introuvable,
un FileNotFoundError est levé au démarrage.

## Persistance (Base de données)

Le projet définit deux tables principales (SQLAlchemy) :

- `model_inputs` : stocke l'objet JSON des features envoyées au modèle.
- `model_outputs`: stocke la prédiction, la probabilité et une référence
  vers `model_inputs`.

Extrait du schéma (UML / PlantUML) :

```plantuml
@startuml
entity model_inputs {
	+ id : int
	--
	features : jsonb
	created_at : timestamp
}

entity model_outputs {
	+ id : int
	--
	prediction : int
	probability : float
	created_at : timestamp
}

model_inputs ||--o{ model_outputs : generates
@enduml
```

SQL (exemples simplifiés)

```sql
CREATE TABLE model_inputs (
	id SERIAL PRIMARY KEY,
	features JSONB NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

CREATE TABLE model_outputs (
	id SERIAL PRIMARY KEY,
	input_id INTEGER NOT NULL REFERENCES model_inputs(id) ON DELETE CASCADE,
	prediction INTEGER NOT NULL CHECK (prediction IN (0,1)),
	probability DOUBLE PRECISION NULL CHECK (probability >= 0 AND probability <= 1),
	created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);
```

## Quelques validations côté ORM

La couche `app/db/models.py` contient des validations détaillées des
features (plages autorisées, cohérences entre âge / expérience / ancienneté,
types, etc.). Ces règles protègent l'intégrité des données persistées.

## Tests

Les tests unitaires se trouvent dans `tests/`. Pour lancer la suite :

```bash
pytest -q
```
