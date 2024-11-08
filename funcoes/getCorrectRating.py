import os
import pickle
import pandas as pd
import numpy as np
import nltk
import math
import re
from funcoes.logMessage import *


started = False
scaler = None

def clean_text(text, stop_words):
    if isinstance(text, str):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        words = nltk.word_tokenize(text) 
        words = [word for word in words if word not in stop_words] 
        return ' '.join(words)
    else:
        return ''  

def convert_tempo_to_numeric(tempo):
    if isinstance(tempo, str):
        tempo = tempo.lower()
        if 'hoje' in tempo:
            return 0
        elif 'ontem' in tempo:
            return 1
        elif 'dia' in tempo:
            dias = re.search(r'(\d+)', tempo)
            return int(dias.group(1)) if dias else 1
        elif 'semana' in tempo:
            semanas = re.search(r'(\d+)', tempo)
            return int(semanas.group(1)) * 7 if semanas else 7
        elif 'mês' in tempo or 'mes' in tempo:
            meses = re.search(r'(\d+)', tempo)
            return int(meses.group(1)) * 30 if meses else 30
        elif 'ano' in tempo:
            anos = re.search(r'(\d+)', tempo)
            return int(anos.group(1)) * 365 if anos else 365
        else:
            return np.nan  
    else:
        return np.nan  

def prepare_data_for_model(df,id):
    global scaler
    stop_words = set(nltk.corpus.stopwords.words('portuguese'))
    
    log(f"Convertendo Tempo - {id}")
    df['tempo'] = df['tempo'].apply(convert_tempo_to_numeric)
    df['tempo'] = df['tempo'].fillna(df['tempo'].median()) 
    
    log(f"Convertendo Local Guide - {id}")
    if df['Local Guide'].dtype == 'bool':
        df['Local Guide'] = df['Local Guide'].astype(int)
    

    
    log(f"Convertendo Avaliação - {id}")
    df['avaliacao'] = df['avaliacao'].apply(lambda x: clean_text(x, stop_words))
    
    
    features_numericas = ['tempo', 'estrelas', 'Local Guide', 'Avaliacoes', 'Classificacoes', 'Fotos', 'Videos', 'Legendas', 'Respostas', 'Edicoes',
                          'Informadas como Incorretas', 'Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R']
    
    X_text = df['avaliacao']
    log(f"Convertendo Campos Numericos - {id}")
    for feature in features_numericas:
        df[feature] = pd.to_numeric(df[feature], errors='coerce')
        df[feature] = df[feature].fillna(df[feature].median())
    
  
    log(f"Normalizando Dados Numericos - {id}")
    X_additional = df[features_numericas]
    

    log(f"Carregando vetorizador - {id}")
    vectorizer = scaler['vectorizer']
    X_text_vectorized = vectorizer.transform(X_text.astype(str))

    
    X_text_df = pd.DataFrame(X_text_vectorized.toarray(), index=df.index)
    
    log(f"Concatenando features adicionais com texto vetorizado - {id}")
    X = pd.concat([X_additional.reset_index(drop=True), X_text_df.reset_index(drop=True)], axis=1)
    X.columns = X.columns.astype(str)

    return X,vectorizer


def predict_fraude_and_save(df,id):

    global scaler

    model_rf = scaler['model_rf']
    scalerobj = scaler['scaler']
    vectorizer = scaler['vectorizer']
    
    log(f"Preparando dados para o modelo - {id}")
    X, _ = prepare_data_for_model(df,id)

    
    log(f"Normalizando dados para o modelo - {id}")
    X_scaled = scalerobj.transform(X)
    
    log(f"Fazendo Previsões - {id}")
    pred_rf = model_rf.predict(X_scaled)

    df['Previsao_Fraude_RF'] = pred_rf

    return df


def handleGetCorrectRating(df, id):
    global started
    if not started:
        log("Baixando pacotes NLTK")
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('punkt_tab')
        log("Obtendo Scaler")
        get_latest_scaler_version()
        started = True
    
    df_resultado = predict_fraude_and_save(df.copy(),id)
    df['Previsao_Fraude_RF'] = df_resultado['Previsao_Fraude_RF']

    log(f"""Resultado da Análise do Estabelecimento {id}
Antes: {math.trunc(df_resultado['estrelas'].mean() * 10) / 10}
Depois: {math.trunc(df_resultado[df_resultado['Previsao_Fraude_RF'] == 0]['estrelas'].mean() * 10) / 10}
Total de Avaliações: {df_resultado.shape[0]}
Fraudes: {(df_resultado['Previsao_Fraude_RF'] == 1).sum()}
""")


    df.to_csv(f'./evaluetedReviews/resultado_fraude_{id}.csv', index=False)
    return math.trunc(df_resultado[df_resultado['Previsao_Fraude_RF'] == 0]['estrelas'].mean() * 10) / 10

def get_latest_scaler_version():
    global scaler
    model_dir = './modelVersions'
    
    model_files = os.listdir(model_dir)
    
    version_files = [f for f in model_files if f.startswith('modelVersion_') and f.endswith('.pkl')]
    
    if not version_files:
        raise Exception("Nenhum scaler encontrado.")
    
    version_numbers = [int(f.split('_')[1].split('.pkl')[0]) for f in version_files]
    
    latest_version = max(version_numbers)
    
    latest_scaler_file = os.path.join(model_dir, f'modelVersion_{latest_version}.pkl')
    
    with open(latest_scaler_file, 'rb') as f:
        scaler = pickle.load(f)
    
    log(f"Scaler versão {latest_version} carregado com sucesso!")
    return scaler

def handleSaveModel():
    global started
    global scaler
    if(started):
        model_dir = 'modelVersions'
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        model_files = os.listdir(model_dir)
        
        version_files = [f for f in model_files if f.startswith('modelVersion_')]
        
        if version_files:
            version_numbers = [int(f.split('_')[1].split('.pkl')[0]) for f in version_files]
            new_version = max(version_numbers) + 1
        else:
            new_version = 1

        new_scaler_file = os.path.join(model_dir, f'modelVersion_{new_version}.pkl')

        with open(new_scaler_file, 'wb') as f:
            pickle.dump(scaler, f)

        log(f"Novo scaler salvo como: {new_scaler_file}")
    else:
        raise Exception("Modelo ainda não foi inicializado")
