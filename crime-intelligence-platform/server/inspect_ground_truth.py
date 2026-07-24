import os
from pathlib import Path
import pandas as pd

root = Path('..') / '..' / 'datathon-2026' / 'Datathon' / 'generator' / 'output'
root = root.resolve()
print('root:', root)
for name in ['CaseFingerprint.csv','CaseLinkResult.csv','EntityMatchResult.csv','GroundTruthCaseLinks.csv','GroundTruthEntityMatches.csv']:
    path = root / name
    print(name, path.exists(), path.stat().st_size if path.exists() else None)
    if path.exists():
        df = pd.read_csv(path)
        print('columns:', list(df.columns))
        print('rows:', len(df))
        print(df.head(2).to_dict(orient='records'))
        print('---')
