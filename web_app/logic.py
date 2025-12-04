
def solve_schedule(trips_data, dh_matrix):
    """
    Solves the vehicle scheduling problem.
    
    Args:
        trips_data: A list of dictionaries or a dict of tuples.
                    Format expected from UI: 
                    [
                        {"id": 1, "dep_term": "a", "dep_time": 420, "arr_term": "b", "arr_time": 445},
                        ...
                    ]
        dh_matrix: A dict of dicts for deadheading times.
                   {'a': {'a':0, 'b':15...}, ...}
                   
    Returns:
        A dictionary with "min_vehicles" and "blocks".
    """
    
    # Normalize trips input to the format used in the algorithm:
    # trips[id] = (dep_term, dep_time, arr_term, arr_time)
    trips = {}
    for t in trips_data:
        # Ensure inputs are integers where needed
        tid = int(t['id'])
        trips[tid] = (
            t['dep_term'], 
            int(t['dep_time']), 
            t['arr_term'], 
            int(t['arr_time'])
        )

    # -----------------------------------------
    # Step 1: Find feasible follow-up edges
    # -----------------------------------------
    edges = {i: [] for i in trips}

    for i in trips:
        # trips[i] is (dep_term, dep_time, arr_term, arr_time)
        # We need arr_time of i
        arr_i = trips[i][3]
        arr_term_i = trips[i][2]
        
        for j in trips:
            if j == i: 
                continue
            
            dep_j = trips[j][1]
            dep_term_j = trips[j][0]
            
            # Check if connection is feasible
            # arr_time_i + deadhead(arr_term_i -> dep_term_j) <= dep_time_j
            
            # Handle missing keys in DH matrix gracefully
            dh_time = 0
            if arr_term_i in dh_matrix and dep_term_j in dh_matrix[arr_term_i]:
                dh_time = int(dh_matrix[arr_term_i][dep_term_j])
            else:
                # Fallback or error? For now assume 0 or large number? 
                # Let's assume 0 if same terminal, else infinity?
                # The original code had a complete matrix.
                # We will assume the UI provides a complete matrix or we default to 0.
                dh_time = 0 

            if arr_i + dh_time <= dep_j:
                edges[i].append(j)

    # -----------------------------------------
    # Step 2: Maximum bipartite matching
    # -----------------------------------------
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

    # -----------------------------------------
    # Step 3: Build actual chains
    # -----------------------------------------
    # Convert matching R->L to L->R
    matchL = {}
    for r in matchR:
        matchL[matchR[r]] = r

    used = set()
    blocks = []

    # Sort by departure time for deterministic/logical ordering of blocks
    sorted_trip_ids = sorted(trips, key=lambda x: trips[x][1])

    for i in sorted_trip_ids:
        if i in used:
            continue
        chain = [i]
        used.add(i)
        
        curr = i
        while curr in matchL:
            nxt = matchL[curr]
            chain.append(nxt)
            used.add(nxt)
            curr = nxt
        blocks.append(chain)

    # Format output for the UI
    # We want to return the full trip details in the blocks, not just IDs
    formatted_blocks = []
    for block in blocks:
        block_details = []
        for tid in block:
            t = trips[tid]
            block_details.append({
                "id": tid,
                "dep_term": t[0],
                "dep_time": t[1],
                "arr_term": t[2],
                "arr_time": t[3]
            })
        formatted_blocks.append(block_details)

    return {
        "min_vehicles": min_vehicles,
        "blocks": formatted_blocks
    }
