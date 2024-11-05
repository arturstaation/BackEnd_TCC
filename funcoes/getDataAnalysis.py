import os
import pandas as pd


def handleDataAnalysis():
    pasta = './evaluetedReviews'


    total_linhas = 0
    total_ult_col_valor_1 = 0
    
    for arquivo in os.listdir(pasta):
        if arquivo.endswith('.csv'):
            df = pd.read_csv(os.path.join(pasta, arquivo))
            
            total_linhas += len(df)
            
            total_ult_col_valor_1 += df.iloc[:, -1].eq(1).sum()
    
    return total_linhas, total_ult_col_valor_1
