import keras
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import plot_model
from sklearn.metrics import accuracy_score, classification_report

# Função para carregar e processar os dados
def load_data():
    url = 'https://raw.githubusercontent.com/CD-CrashTest/Crash_Test/refs/heads/main/scrappingNewDf.csv'
    data = pd.read_csv(url)
    data['Kerb Weight'] = data['Kerb Weight'].str.replace('kg', '').astype(float)
    return data

# Função de pré-processamento
def preprocess_data(data):
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        mean = data[col].mean()
        std_dev = data[col].std()
        data[col] = data[col].apply(lambda x: np.random.uniform(mean - std_dev, mean + std_dev) if pd.isna(x) else x)
    return data

def train_keras_model(data):
    # Selecionar as features relevantes
    features_selected = ['Kerb Weight', 'Safety Features', 'CRS Installation Check', 'Class', 'Seatbelt Reminder']
    features = data[features_selected]

    # Converter features categóricas para numéricas usando one-hot encoding
    categorical_features = ['Class', 'Safety Features', 'CRS Installation Check', 'Seatbelt Reminder'] #Especificar as colunas categoricas
    numerical_features = ['Kerb Weight'] #Especificar as colunas numericas

    # Converter as features categóricas para numéricas usando one-hot encoding
    encoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    encoded_features = encoder.fit_transform(features[categorical_features])

    # Criar um novo dataframe com as features codificadas
    encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(categorical_features))

    # Concatenar as features numéricas com as codificadas
    X = pd.concat([features[numerical_features], encoded_df], axis=1)

    # Converter o rating para numérico (se necessário)
    y = data['rating'].astype(int)

    # Dividir os dados em treinamento e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalizar os dados numéricos
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Criar o modelo
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(X_train_scaled.shape[1],)))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(6, activation='softmax')) # 6 classes (0 a 5)

    # Compilar o modelo
    optimizer = keras.optimizers.Adam(learning_rate=0.01) # Altere o valor 0.001 para o learning rate desejado

    # Compilar o modelo com o otimizador definido
    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    # Treinar o modelo
    history = model.fit(X_train_scaled, y_train, epochs=60, batch_size=200, validation_split=0.2)

    # Avaliar o modelo
    loss, accuracy = model.evaluate(X_test_scaled, y_test, verbose=0)
    y_pred = (model.predict(X_test_scaled) > 0.5).astype(int)
    # report = classification_report(y_test, y_pred)
    # print(f'Acurácia do modelo: {accuracy}')
    return model, encoder, scaler, accuracy, history

def user_input_features():
    st.header('Insira os dados do veículo para previsão')

    # Entrada dos dados
    kerb_weight = st.number_input("Peso do veículo em Kg", min_value=500.0, max_value=3000.0, step=0.1)
    safety_features = st.number_input("Nota dos equipamentos de segurança (0-10)", min_value=0.0, max_value=10.0, step=0.1)
    crs_installation = st.number_input("Nota da facilidade para cadeirinha infantil (0-12)", min_value=0.0, max_value=12.0, step=0.1)
    vehicle_class = st.text_input("Classe do veículo")
    seatbelt_reminder = st.selectbox("Aviso de cinto de segurança", options=['sim', 'nao'])

    # Criação do DataFrame com os dados do usuário
    user_input = pd.DataFrame({
        'Kerb Weight': [kerb_weight],
        'Safety Features': [safety_features],
        'CRS Installation Check': [crs_installation],
        'Class': [vehicle_class],
        'Seatbelt Reminder': [seatbelt_reminder]
    })
    return user_input

# Interface Streamlit
st.title("Análise de Crash Test de Veículos com Keras")
st.write("Este aplicativo permite carregar, processar dados e treinar um modelo Keras.")

if st.button("Carregar e processar dados"):
    data = load_data()
    st.write("Dados carregados com sucesso!")
    st.write("Pré-processando dados...")
    data = preprocess_data(data)
    st.write("Dados processados!")
    st.write(data.head())

user_input = user_input_features()

if st.button("Rodar Validação"):
    st.write("Iniciando treinando do modelo Keras!")
    data = load_data()
    data = preprocess_data(data)
    model, encoder, scaler, accuracy, history = train_keras_model(data)
    st.write("Modelo Keras treinado!")
    st.write(f"Acurácia no teste: {accuracy:.2f}")

    # Exibir gráfico de histórico de treinamento
    st.write("Histórico de Treinamento")
    st.line_chart(pd.DataFrame(history.history))

    # Codificação e escalonamento dos dados do usuário
    user_encoded = encoder.transform(user_input[['Class', 'Safety Features', 'CRS Installation Check', 'Seatbelt Reminder']])
    X_user = pd.concat([user_input[['Kerb Weight']], pd.DataFrame(user_encoded, columns=encoder.get_feature_names_out())], axis=1)
    X_user_scaled = scaler.transform(X_user)

    # Previsão
    prediction = model.predict(X_user_scaled)
    predicted_class = np.argmax(prediction)

    # Exibir resultado
    st.write("### Resultado da Previsão")
    st.write("Entrada do usuário:")
    st.write(user_input)
    st.write(f"Previsão do Rating: {predicted_class}")