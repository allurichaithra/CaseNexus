import os
import pandas as pd

root = os.path.abspath(os.path.join('..','..','datathon-2026','Datathon','generator','output'))
print('root:', root)
files = ['CaseFingerprint.csv','CaseLinkResult.csv','EntityMatchResult.csv','GroundTruthCaseLinks.csv','GroundTruthEntityMatches.csv']
for name in files:
    path = os.path.join(root, name)
    print(name, os.path.exists(path), os.path.getsize(path) if os.path.exists(path) else None)
    if os.path.exists(path):
        df = pd.read_csv(path)
        print('columns:', df.columns.tolist())
        print('rows:', len(df))
        print(df.head(2).to_dict(orient='records'))
        print('---')
