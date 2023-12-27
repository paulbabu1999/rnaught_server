# utils.py
import json

def find_probability(a, virus_type):
    return 0.92 / int(a[1])

def findsource(runquery, user_id, virus_type):
    source = None
    query = f"MATCH(a:Person {{id: '{user_id}'}}),(b:{virus_type}),p = shortestPath((a)-[r:contact*]-(b)) RETURN r"
    fr = runquery(query)[0]['data']

    if len(fr) == 0:
        return None

    fr = fr.split("\n")
    fr = min(fr, key=len)
    fr = json.loads(fr)
    fr = fr['r']

    q = f"MATCH(n {{id:'{user_id}'}}) RETURN id(n)"
    val = runquery(q)[0]['id(n)']
    visited = set()

    visited.add(str(val))
    prev = {}
    i = fr[0]
    contact_time = (i['properties']['contact_times']).split("\n")[-1]

    if i['start']['id'] in visited:
        prev[i['end']['id']] = int(contact_time.split(":")[0])
        visited.add(i['end']['id'])
    else:
        prev[i['start']['id']] = int(contact_time.split(":")[0])
        visited.add(i['start']['id'])

    for i in fr[1:]:
        contact_time = int(((i['properties']['contact_times']).split("\n")[0]).split(":")[0])

        if i['start']['id'] in visited:
            end_id = i['end']['id']
            visited.add(i['end']['id'])
            start_id = i['start']['id']
        else:
            end_id = i['start']['id']
            visited.add(i['start']['id'])
            start_id = i['end']['id']

        if contact_time <= prev[start_id]:
            prev[end_id] = int(((i['properties']['contact_times']).split("\n")[-1]).split(":")[0])
        else:
            source = end_id
            return source

    return source

def five_level(runquery, current_time, find_probability, user_id, virus_type, is_source):
    val = 1
    s_prob = f"u.p_{virus_type[-1]}"
    v_type = f"u.{virus_type}"

    q = f"MATCH(u) WHERE u.id='{user_id}' RETURN labels(u)"
    fr = runquery(q)[0]['labels(u)']
    temp = ":".join(fr)
    temp = f"u:{temp}"

    if is_source:
        val = 0.5

    q = f"MATCH(u) WHERE u.id='{user_id}' REMOVE {temp} SET u:Positive:{virus_type}:Person SET {s_prob}={val}"
    runquery(q)

    query = f"MATCH p=({{id:'{user_id}'}})-[r:contact*..5]-(fr) RETURN relationships(p), length(p), nodes(p)"
    fr = runquery(query)[0]['data']

    if fr:
        fr = fr.split("\n")
        fr = list(map(json.loads, fr))
        dat = []
        visited = set()
        prev_times = {}

        for i in fr:
            dat.append((i['relationships(p)'][-1], i['length(p)']))

        dat.sort(key=lambda x: x[1])

        for i in dat:
            if i[1] > 1:
                if i[0]['start']['id'] in visited and i[0]['end']['id'] in visited:
                    continue

                if i[0]['start']['id'] in prev_times:
                    id_start = i[0]['start']['id']
                    id_end = i[0]['end']['id']
                elif i[0]['end']['id'] in prev_times:
                    id_start = i[0]['end']['id']
                    id_end = i[0]['start']['id']
                else:
                    continue

                visited.add(id_end)
                first_contact_times = i[0]['properties']['contact_times'].split("\n")
                temp = []

                for p in first_contact_times:
                    temp.append(int(p.split(":")[0]))

                flag = 0
                first_contact_times = temp

                for j in range(len(first_contact_times)):
                    if first_contact_times[j] >= prev_times[id_start]:
                        contact_time = first_contact_times[j]
                        flag = 1
                        break

                if flag:
                    prob = find_probability(i, virus_type)
                    q = f"MATCH(u) WHERE id(u)={id_end} RETURN labels(u), {s_prob}"
                    q_res = runquery(q)[0]

                    prob_end = q_res[s_prob]

                    if prob > prob_end:
                        prev_times[id_end] = contact_time
                        q = f"MATCH (u:Person) WHERE id(u)={id_end} SET {s_prob}={prob} SET u:{virus_type}"
                        runquery(q)

            else:
                first_contact_times = i[0]['properties']['contact_times'].split("\n")
                id_start = i[0]['start']['id']
                id_end = i[0]['end']['id']
                visited.add(id_end)
                visited.add(id_start)

                q = f"MATCH(u) WHERE id(u)={id_start} RETURN labels(u), {s_prob}"
                q_res = runquery(q)[0]
                labels_start = q_res['labels(u)']
                prob_start = q_res[s_prob]

                q = f"MATCH(u) WHERE id(u)={id_end} RETURN labels(u), {s_prob}"
                q_res = runquery(q)[0]
                labels_end = q_res['labels(u)']
                prob_end = q_res[s_prob]

                if current_time() - int(first_contact_times[-1].split(":")[0]) < 14 * 3600 and prob_start != prob_end:
                    prob = find_probability(i, virus_type)

                    if prob_start < prob_end and prob_start < prob:
                        prev_times[id_start] = int(first_contact_times[-1].split(":")[0])
                        q = f"MATCH (u) WHERE id(u)={id_start} SET {s_prob}={prob} SET u:{virus_type}"
                        runquery(q)
                    elif prob_end < prob:
                        prev_times[id_end] = int(first_contact_times[-1].split(":")[0])
                        q = f"MATCH (u) WHERE id(u)={id_end} SET {s_prob}={prob} SET u:{virus_type}"
                        runquery(q)

    return 201
