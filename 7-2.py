from collections import deque, defaultdict

# -----------------------------
# Input data
# -----------------------------
trips = {
    1: ("a",  7*60+0,  "b",  7*60+25),
    2: ("d",  7*60+0,  "a",  7*60+35),
    3: ("b",  7*60+15, "c",  8*60+15),
    4: ("c",  7*60+30, "d",  8*60+35),
    5: ("a",  7*60+35, "d",  8*60+0),
    6: ("d",  8*60+0,  "a",  8*60+30),
    7: ("a",  8*60+35, "d",  9*60+5),
    8: ("c",  9*60+5,  "d", 10*60+0)
}

DH = {
    'a': {'a':0, 'b':15, 'c':30, 'd':25},
    'b': {'a':20, 'b':0, 'c':40, 'd':30},
    'c': {'a':25, 'b':35, 'c':0, 'd':45},
    'd': {'a':20, 'b':25, 'c':35, 'd':0}
}

# -----------------------------
# Build adjacency for feasible follow-ups
# i -> j if arrival + DH <= dep(j)
# -----------------------------
pairs = defaultdict(list)
for i in trips:
    dep_i, arr_i = trips[i][1], trips[i][3]
    term_i = trips[i][2]
    for j in trips:
        if i == j: continue
        dep_j = trips[j][1]
        term_j = trips[j][0]
        if arr_i + DH[term_i][term_j] <= dep_j:
            pairs[i].append(j)

# -----------------------------
# Build flow network (bipartite representation)
# left nodes = i_out, right nodes = i_in
# -----------------------------
nodes = set()
capacity = defaultdict(lambda: defaultdict(int))

source = "s"
sink   = "t"

for i in trips:
    L = f"L{i}"
    R = f"R{i}"
    nodes.add(L); nodes.add(R)

    # connect source -> L(i)
    capacity[source][L] = 1
    # connect R(i) -> sink
    capacity[R][sink] = 1

# edges L(i) -> R(j)
for i in pairs:
    for j in pairs[i]:
        capacity[f"L{i}"][f"R{j}"] = 1

nodes.add(source)
nodes.add(sink)

# -----------------------------
# Max-flow: Edmonds-Karp
# -----------------------------
def bfs():
    parent = {n: None for n in nodes}
    parent[source] = source
    q = deque([source])
    while q:
        u = q.popleft()
        for v in capacity[u]:
            if capacity[u][v] > 0 and parent[v] is None:
                parent[v] = u
                if v == sink:
                    return parent
                q.append(v)
    return None

flow = 0
while True:
    parent = bfs()
    if not parent:
        break
    flow += 1
    v = sink
    while v != source:
        u = parent[v]
        capacity[u][v] -= 1
        capacity[v][u] += 1
        v = u

print("Maximum matching =", flow)
min_vehicles = len(trips) - flow
print("Minimum vehicles required =", min_vehicles)

# -----------------------------
# Extract chains (blocks)
# -----------------------------
used = set()
chains = []

# build reverse edges (actual matching)
match = {}
for L in [f"L{i}" for i in trips]:
    for R in capacity[L]:
        if R.startswith("R") and capacity[R][L] == 1:  # residual means matched
            i = int(L[1:])
            j = int(R[1:])
            match[i] = j

# build chains
for i in trips:
    if i not in used:
        chain = [i]
        used.add(i)
        while chain[-1] in match:
            nxt = match[chain[-1]]
            chain.append(nxt)
            used.add(nxt)
        chains.append(chain)

print("Blocks:", chains)
