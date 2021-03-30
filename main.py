import argparse
import pandas as pd
import numpy as np
import os
#import math

def v2(filename):
    if os.path.isfile(filename.split('.')[0] + '.csv'):
        df = pd.read_csv(filename.split('.')[0] + '.csv')
    else:
        xls = pd.ExcelFile(filename)
        df = pd.read_excel(xls, 'From start_date to the date')
        del df['QuarterRank'], df['Engagement'], df['GamePlay'], df['CPI'], df['UA'], df['Rev']
        df = df.sort_values('quarter')
        df['QuarterRank'] = df.groupby(['name', 'platform']).cumcount() + 1
        df.sort_index(inplace=True)
        df['Engagement'] = df.apply(lambda x: round(0.5 * x.d1 + 0.1 * x.d2 + 0.1 * x.d3 + 0.3 * x.d7, 2), axis=1)
        df['GamePlay'] = df.apply(lambda x: round(x.sessions * x.duration, 2), axis=1)
        df['CPI'] = df.apply(lambda x: x.cpi, axis=1)
        df['UA'] = df.apply(lambda x: round((x.ctr + x.cvr + x.cti) / 3, 2), axis=1)
        df['Rev'] = df.apply(lambda x: x.revenue, axis=1)
        df = df[['quarter', 'name', 'bundleid', 'platform', 'genre', 'subgenre', 'QuarterRank', 'Engagement', 'GamePlay', 'CPI', 'UA', 'Rev']]
        df['Eng-Rate'] = df.apply(lambda x: -1 if x.QuarterRank == 1 else (-1 if df.iloc[x.name - 1].Engagement == 0 else round((x.Engagement - df.iloc[x.name - 1].Engagement) / df.iloc[x.name - 1].Engagement, 2)), axis=1)
        df['GPlay-Rate'] = df.apply(lambda x: -1 if x.QuarterRank == 1 else (-1 if df.iloc[x.name - 1].GamePlay == 0 else round((x.GamePlay - df.iloc[x.name - 1].GamePlay) / df.iloc[x.name - 1].GamePlay, 2)), axis=1)
        df['CPI-Rate'] = df.apply(lambda x: -1 if x.QuarterRank == 1 else (-1 if df.iloc[x.name - 1].CPI == 0 else round((x.CPI - df.iloc[x.name - 1].CPI) / df.iloc[x.name - 1].CPI, 2)), axis=1)
        df['UA-Rate'] = df.apply(lambda x: -1 if x.QuarterRank == 1 else (-1 if df.iloc[x.name - 1].UA == 0 else round((x.UA - df.iloc[x.name - 1].UA) / df.iloc[x.name - 1].UA, 2)), axis=1)
        df['Rev-Rate'] = df.apply(lambda x: -1 if x.QuarterRank == 1 else (-1 if df.iloc[x.name - 1].Rev == 0 else round((x.Rev - df.iloc[x.name - 1].Rev) / df.iloc[x.name - 1].Rev, 2)), axis=1)
        df.to_csv(filename.split('.')[0] + '.csv', index=False)
    return df

def dist(x, y):
    x = np.array([x['Engagement'], x['GamePlay'], x['CPI'], x['UA']])
    y = np.array([y[0],y[1],y[2],y[3]])
    return np.linalg.norm(x-y)
    

def main(df, query, K):
    df = df.loc[(df['genre'] == query[0]) & (df['subgenre'] == query[1])]
    if query[2] != 'both':
        df = df.loc[df['platform'] == query[2]]
    df['dist'] = df.apply(lambda x: dist(x, query[3]), axis=1)
    top = df.sort_values('dist').head(K)
    ans = []
    for index, row in top.iterrows():
        temp  = df.loc[(df['name'] == row['name']) & (df['platform'] == row['platform']) & (df['QuarterRank'] >= row.QuarterRank)]
        ans.append(temp)
    return pd.concat(ans)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('--f', dest='filename', type=str, help='Input filename')
    parser.add_argument('--g', dest='genre', type=str, help='Genre')
    parser.add_argument('--s', dest='subgenre', type=str, help='SubGenre')
    parser.add_argument('--k', dest='K', type=int, help='Number of neighbors', default=3)
    parser.add_argument('--p', dest='platform', type=str, help='Platform', default='both')
    parser.add_argument('--v', dest='values', type=str, help='Values')

    args = parser.parse_args()
    df = v2(args.filename)
    df = main(df, (args.genre, args.subgenre, args.platform, [float(item) for item in args.values.split(',')]), args.K)
    print(df)
