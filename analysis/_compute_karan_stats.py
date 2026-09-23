import csv,statistics
p=r'c:\Users\nanda\Downloads\Multilingual_UPI_Complaint_Assistant\data\raw_data\karanverma19_multilingual_customer_support_intent_dataset.csv'
rows=list(csv.DictReader(open(p,encoding='utf-8')))
texts=[r['query'].strip() for r in rows]
lengths=[len(t) for t in texts]
mean=sum(lengths)/len(lengths) if lengths else 0
median=statistics.median(lengths) if lengths else 0
from collections import Counter
c=Counter(texts)
unique_dup_count=sum(1 for v in c.values() if v>1)
print('rows',len(rows))
print('mean_char_len',mean)
print('median_char_len',median)
print('unique_duplicate_texts',unique_dup_count)
print('sample_duplicates')
for t,count in c.most_common():
    if count>1:
        print(count,'x',t)
