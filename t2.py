import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder, StandardScaler, PolynomialFeatures
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
import numpy as np

# Carregar o dataset
file_path = 'scrappingNewDf.csv'  # Atualize com o caminho correto do arquivo
data = pd.read_csv(file_path)
data['Kerb Weight'] = data['Kerb Weight'].str.replace('kg', '').astype(float)

# Preprocessamento dos dados
# Remover colunas irrelevantes e linhas com muitos valores nulos
# data_cleaned = data.drop(columns=["Tested Model", "VIN From Which Rating Applies", "Class", "Safety Features.1",
#                                   "CRS Installation Check.1", "Pelvis", "Femur", "Knee & Tibia"])

# Selecting relevant numeric columns with sufficient non-null values
selected_columns = [
    'Year Of Publication', 'Frontal Offset Deformable Barrier', 'Whiplash Rear Impact', 
    'Lateral Impact', '18 months old child', '36 months old child', 'VRU Impact Protection', 
    'Crash Test Performance', 'Safety Features', 'CRS Installation Check', 'Speed Assistance', 
    'Electronic Stability Control', 'Seatbelt Reminder', 'Lane Support', 'AEB Inter-Urban', 
    'Head Impact', 'Pelvis Impact', 'Leg Impact', 'rating', 'Kerb Weight', 'Body Type'
]
data_cleaned = data[selected_columns]


# Remover colunas com mais de 50% de valores nulos
threshold = 0.5 * len(data_cleaned)
data_cleaned = data_cleaned.dropna(axis=1, thresh=threshold)

# Remover linhas com valores nulos restantes
data_cleaned = data_cleaned.dropna()

# Codificar variáveis categóricas
label_encoders = {}
for column in data_cleaned.select_dtypes(include=['object']).columns:
    le = LabelEncoder()
    data_cleaned[column] = le.fit_transform(data_cleaned[column])
    label_encoders[column] = le

# Separar recursos e rótulos
X = data_cleaned.drop(columns=["rating"])
y = data_cleaned["rating"]

# Adicionar características polinomiais para aumentar a complexidade do modelo
poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
X_poly = poly.fit_transform(X)

# Dividir o conjunto de dados em treino e teste
X_train, X_test, y_train, y_test = train_test_split(X_poly, y, test_size=0.2, random_state=42)

# Criar um pipeline para incluir a normalização dos dados e o modelo de regressão
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('rf', RandomForestRegressor(random_state=42))
])

# Definir a grade de parâmetros para otimização
param_grid_optimized = {
    'rf__n_estimators': [100, 200, 300],
    'rf__max_depth': [20, 30, None],
    'rf__min_samples_split': [2, 5, 10],
    'rf__min_samples_leaf': [1, 2, 4],
    'rf__max_features': ['auto', 'sqrt', 'log2']
}

# Otimizar hiperparâmetros usando GridSearchCV
grid_search_optimized = GridSearchCV(estimator=pipeline, param_grid=param_grid_optimized, cv=5, n_jobs=-1, verbose=2, scoring='r2')
grid_search_optimized.fit(X_train, y_train)

# Melhor modelo otimizado
best_pipeline = grid_search_optimized.best_estimator_

# Avaliar o modelo no conjunto de teste
y_pred_optimized = best_pipeline.predict(X_test)
mse_optimized = mean_squared_error(y_test, y_pred_optimized)
r2_optimized = r2_score(y_test, y_pred_optimized)

print(f"Mean Squared Error: {mse_optimized}")
print(f"R2 Score: {r2_optimized}")

# Realizar cross-validation para acurácia (R²)
cross_val_scores = cross_val_score(best_pipeline, X_poly, y, cv=5, scoring='r2')
mean_cross_val_score = np.mean(cross_val_scores)

print(f"Cross-Validation R2 Score: {mean_cross_val_score}")
