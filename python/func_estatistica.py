import pandas as pd

def estatisticas(coluna:pd.Series):
    estatistica_coluna = coluna.describe()

    MAD = (coluna - estatistica_coluna.loc['mean']).abs().mean()
    CV = estatistica_coluna.loc['std']/estatistica_coluna.loc['mean']
    IQR = estatistica_coluna.loc['75%'] - estatistica_coluna.loc['25%']
    outlier_max = estatistica_coluna.loc['75%'] + (1.5*IQR)
    outlier_min = estatistica_coluna.loc['25%'] - (1.5*IQR)

    valores = [estatistica_coluna['count'],estatistica_coluna.loc['mean'],estatistica_coluna.loc['std'],estatistica_coluna.loc['min'],estatistica_coluna.loc['max'],estatistica_coluna.loc['25%'],estatistica_coluna.loc['50%'], estatistica_coluna.loc['75%'],MAD, CV, IQR, outlier_max, outlier_min]
    indexes = ['Count','mean','std','min','max','25%','mediana','75%','MAD','CV','IQR','outlier_max','outlier_min']
    return pd.Series(valores, index = indexes)