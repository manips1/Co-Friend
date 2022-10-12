import pandas as pd

df = pd.read_csv('problems.csv')
li = df.to_numpy()

# 한 row씩 불러오기
result = []
for row in li:
    # nan 제거
    row_list = pd.DataFrame(row).dropna()
    row_list = row_list.to_numpy()

    # prompt & completion
    comp = row_list[0][0]
    comp.replace('"', '\\"')

    prom = 'Create a python problem sentence about '
    for item in row_list[1:]:
        prom += '{} and '.format(item[0])
    prom = prom[:-5]
    prom += '.'

    result.append('{{"prompt":"{}", "completion":"{}"}}'.format(prom, comp))


# 파일 생성
f = open("data.jsonl", 'w')
for item in result:
    f.write(item+'\n')
f.close()

