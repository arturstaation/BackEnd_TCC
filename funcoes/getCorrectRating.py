import os
import pickle
import pandas as pd
import numpy as np
import nltk
import re


started = False
scaler = None  # Inicialmente, será o scaler que vamos carregar

def clean_text(text, stop_words):
    if isinstance(text, str):
        text = text.lower()  # Converter para minúsculas
        text = re.sub(r'[^\w\s]', '', text)  # Remover pontuação
        words = nltk.word_tokenize(text)  # Tokenizar as palavras
        words = [word for word in words if word not in stop_words]  # Remover stopwords
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

def prepare_data_for_model(df, scaler):
    stop_words = set(nltk.corpus.stopwords.words('portuguese'))
    
    df['tempo'] = df['tempo'].apply(convert_tempo_to_numeric)
    df['tempo'].fillna(df['tempo'].median(), inplace=True)  # Preencher valores nulos com a mediana
    
    if df['Local Guide'].dtype == 'bool':
        df['Local Guide'] = df['Local Guide'].astype(int)
    
    df['avaliacao'] = df['avaliacao'].apply(lambda x: clean_text(x, stop_words))
    
    # Definir colunas numéricas
    features_numericas = ['tempo', 'estrelas', 'Local Guide', 'Avaliacoes', 'Classificacoes', 'Fotos', 'Videos', 'Legendas', 'Respostas', 'Edicoes',
                          'Informadas como Incorretas', 'Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R']
    
    for feature in features_numericas:
        df[feature] = pd.to_numeric(df[feature], errors='coerce')
        df[feature].fillna(df[feature].median(), inplace=True)
    
    # Selecionar os dados numéricos para normalização
    X_additional = df[features_numericas]
    
    # Aplicar o scaler carregado
    X_scaled = scaler.transform(X_additional)

    # Retornar os dados escalados
    return X_scaled

def predict_fraude_and_save(df):
    global scaler

    # Preparar os dados usando apenas o scaler
    X_scaled = prepare_data_for_model(df, scaler)

    # Para este exemplo, apenas salvamos o dataframe escalado
    df_scaled = pd.DataFrame(X_scaled, columns=['tempo', 'estrelas', 'Local Guide', 'Avaliacoes', 'Classificacoes', 'Fotos', 'Videos', 'Legendas', 'Respostas', 'Edicoes',
                                                'Informadas como Incorretas', 'Lugares Adicionadas', 'Estradas Adicionadas', 'Informacoes Verificadas', 'P/R'])
    
    df_scaled['Previsao_Fraude'] = 'Indeterminado'  # Placeholder para o resultado final

    # Retornar o dataframe escalado como resultado
    return df_scaled

def handleGetCorrectRating(df, id):
    global started
    global scaler
    if not started:
        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('punkt_tab')
        scaler = get_latest_scaler_version()
        started = True
    df_resultado = predict_fraude_and_save(df)
    df_resultado.to_csv(f'../evaluetedReviews/resultado_fraude_{id}.csv', index=False)

def get_latest_scaler_version():
    model_dir = './modelVersions'
    
    # Listar os arquivos no diretório
    model_files = os.listdir(model_dir)
    
    # Filtrar arquivos que seguem o padrão 'scaler_vX.pkl'
    version_files = [f for f in model_files if f.startswith('modelVersion_') and f.endswith('.pkl')]
    
    if not version_files:
        raise Exception("Nenhum scaler encontrado.")
    
    # Extrair o número da versão do nome do arquivo
    version_numbers = [int(f.split('_')[1].split('.pkl')[0]) for f in version_files]
    
    # Encontrar a maior versão
    latest_version = max(version_numbers)
    
    # Carregar o scaler mais recente
    latest_scaler_file = os.path.join(model_dir, f'modelVersion_{latest_version}.pkl')
    
    with open(latest_scaler_file, 'rb') as f:
        scaler = pickle.load(f)
    
    print(f"Scaler versão {latest_version} carregado com sucesso!")
    return scaler

def save_new_scaler_version(scaler, model_dir='modelVersion'):
    global started
    if(started):
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

        print(f"Novo scaler salvo como: {new_scaler_file}")
    else:
        raise Exception("Modelo ainda não foi inicializado")
