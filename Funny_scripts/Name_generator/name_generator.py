import random
from config import male_names, last_names, female_names

for i in range(20):
    name = random.choice(male_names)
    family = random.choice(last_names)
    n = random.randrange(2, 4)
    k=int(max(len(i) for i in last_names)/2+max(len(i) for i in male_names)/2)+3
    print(f'Original name: {name+" "+family: <{k}} Changed name: {family[:n]+name[n:]+" "+name[:n]+family[n:]}')



