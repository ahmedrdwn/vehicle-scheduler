
# Trips: (dep_terminal, dep_time, arr_terminal, arr_time)


trips = {
    1: ("a", 7*60+0,  "b", 7*60+25),
    2: ("d", 7*60+0,  "a", 7*60+35),
    3: ("b", 7*60+15, "c", 8*60+15),
    4: ("c", 7*60+30, "d", 8*60+35),
    5: ("a", 7*60+35, "d", 8*60+0),
    6: ("d", 8*60+0,  "a", 8*60+30),
    7: ("a", 8*60+35, "d", 9*60+5),
    8: ("c", 9*60+5,  "d", 10*60+0)
}


# Deadheading times


DH = {
    'a': {'a':0, 'b':15, 'c':30, 'd':25},
    'b': {'a':20, 'b':0, 'c':40, 'd':30},
    'c': {'a':25, 'b':35, 'c':0, 'd':45},
    'd': {'a':20, 'b':25, 'c':35, 'd':0}
}


# Step 1: Find feasible follow-up edges

edges = {i: [] for i in trips}

for i in trips:
    dep_i, arr_i = trips[i][1], trips[i][3]
    arr_term = trips[i][2]
    for j in trips:
        if j == i: 
            continue
        dep_j = trips[j][1]
        dep_term = trips[j][0]
        if arr_i + DH[arr_term][dep_term] <= dep_j:
            edges[i].append(j)



matchR = {}   # maps right-node trip j to left-node trip i

def bpm(u, seen):
    for v in edges[u]:
        if v not in seen:
            seen.add(v)
            if v not in matchR or bpm(matchR[v], seen):
                matchR[v] = u
                return True
    return False

result = 0
for i in trips:
    if bpm(i, set()):
        result += 1

min_vehicles = len(trips) - result
print("Minimum vehicles required =", min_vehicles)


# Step 3: Build actual chains

# Convert matching R→L to L→R
matchL = {}
for r in matchR:
    matchL[matchR[r]] = r

used = set()
blocks = []

for i in sorted(trips, key=lambda x: trips[x][1]):
    if i in used:
        continue
    chain = [i]
    used.add(i)
    while chain[-1] in matchL:
        nxt = matchL[chain[-1]]
        chain.append(nxt)
        used.add(nxt)
    blocks.append(chain)

print("Blocks =", blocks)
