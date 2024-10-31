import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Carregar os dados
file_path = 'scrappingNewDf.csv'  # Substitua pelo caminho do seu arquivo
data = pd.read_csv(file_path)

# Remover 'kg' da coluna 'Kerb Weight' e converter para numérico
data['Kerb Weight'] = data['Kerb Weight'].str.replace('kg', '').astype(float)

# Preencher valores ausentes nas colunas numéricas com valores aleatórios entre média ± desvio padrão
numeric_cols = data.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    mean = data[col].mean()
    std_dev = data[col].std()
    data[col] = data[col].apply(lambda x: np.random.uniform(mean - std_dev, mean + std_dev) if pd.isna(x) else x)

# Separar as features e a variável alvo
features = data.select_dtypes(include=[np.number]).drop(columns=['rating'], errors='ignore')
target = data['rating']

# Dividir os dados em conjuntos de treino e teste
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Inicializar e treinar o classificador Random Forest
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# Fazer previsões e avaliar o modelo
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

# Exibir resultados
print("Acurácia:", accuracy)
print("Relatório de Classificação:\n", report)
