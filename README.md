# AgriLens SL: Highland Crops Yield & Production Forecasting System 🇱🇰🌾

> A full-stack, machine-learning-driven agricultural intelligence platform tailored for Sri Lanka. The application predicts crop production and yield across districts based on historical time-series data, cultivation extent, crop types, and seasonal patterns (Yala / Maha).

---

## 👥 Team Members & Contribution Governance
This project is developed as a collaborative group assignment adhering to strict academic standards, with balanced machine learning pipeline contributions across all 4 members:

- **Sathindu**: Data Ingestion, Dataset Auditing, Cleaning & Stratified Splitting (Notebook Steps 1, 2, 4, 6).
- **Lahiru**: Exploratory Data Analysis (EDA) & 6 Domain-Specific Feature Engineering Techniques (Notebook Steps 3, 5).
- **Visun**: Multi-Model Benchmarking (5 Classifiers/Regressors) & Stratified 5-Fold Cross-Validation (Notebook Steps 7, 8).
- **Prashan**: Cost-Sensitive Model Evaluation, Optuna Hyperparameter Optimization & Pipeline Serialization (`.pkl`) (Notebook Steps 9, 10, 11).

---

## 🚀 Key Features
- **Predictive ML Pipeline:** Rigorous data cleaning, feature engineering (yield ratios, lag features, scaling, encoding), and multi-model benchmarking (Random Forest, XGBoost, Linear Models).
- **Future Forecasting:** Ability to predict crop production for upcoming years (e.g., 2026, 2027) based on expected land extent and seasonal conditions.
- **REST API Backend:** Built with Python FastAPI to handle inference requests and serve real-time predictions.
- **Interactive Frontend Dashboard:** Modern UI allowing agricultural officers and farmers to input parameters and instantly view production estimates.

---

## 🛠️ Tech Stack
- **Machine Learning:** Python, Scikit-Learn, Pandas, NumPy, XGBoost, Optuna, Joblib
- **Backend API:** FastAPI, Uvicorn, Pydantic
- **Frontend:** React / Vite / Tailwind CSS (or Streamlit for rapid prototyping)
- **Version Control:** Git & GitHub (Monorepo Architecture)

---

## 📂 Monorepo Structure
```text
agro-forecast-sl/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI routers & endpoints
│   │   ├── models/          # Pydantic schemas
│   │   └── services/        # ML inference and data services
│   ├── model/               # Serialized .pkl pipeline & metadata
│   └── requirements.txt
├── frontend/                # React / Vite UI dashboard
├── notebooks/               # Jupyter Notebook (End-to-end 11-step ML pipeline)
├── docs/                    # Academic project documentation & implementation plans
└── docker-compose.yml       # Full-stack containerization setup


### 📊 11-Step ML Development Lifecycle

* **Problem Definition:** Agricultural planning & production forecasting in Sri Lanka.
* **Data Collection:** Official Department of Census and Statistics highland crops dataset.
* **Data Understanding:** Target distribution and time-series trend analysis.
* **Data Cleaning:** Handling missing values, duplicates, and outlier treatment.
* **Feature Engineering:** Implementation of 6+ domain-specific features.
* **Dataset Splitting:** Stratified train-val-test splitting to prevent data leakage.
* **Algorithm Selection:** Benchmarking 5 diverse regression/time-series models.
* **Model Training:** 5-fold cross-validation and learning curve monitoring.
* **Model Evaluation:** MAE, RMSE, and $R^2$ Score analysis.
* **Model Optimization:** Hyperparameter tuning using Optuna.
* **Deployment & Export:** Pipeline serialization (`pipeline.pkl`) and FastAPI integration.

---

### 📜 License
This project is developed for academic evaluation purposes under the Machine Learning Module.
