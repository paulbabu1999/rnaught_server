import uuid
from flask import Flask,request,jsonify
from neo4j import GraphDatabase, basic_auth
from datetime import datetime
import json
from collections import defaultdict
def current_time():
    now = datetime.now()
 
    

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d %m %Y %H %M %S")
    dt_string=list(map(int,dt_string.split(" ")))
    
    ltime=dt_string[-2]+dt_string[-3]*60 + dt_string[0]*3600+dt_string[1]*3600*30+dt_string[2]*365*3600
    return ltime


def find_probability(a,virus_type):
    return .92/int(a[1])

 
    
    

    #to do:consider other factors to find probability
      
app=Flask(__name__)
people={}
id_new=0 
driver = GraphDatabase.driver(
  "bolt://3.238.138.75:7687",
  auth=basic_auth("neo4j", "gloves-blueprint-badge"),max_connection_lifetime=200)

def runquery(q):
  session=driver.session()
  fr=session.run(q)
  return fr.data()
def findsource(user_id,virus_type):
    source=None
    query="CALL apoc.export.json.query("
    q="MATCH(a:Person { "+f"id: '{user_id}' "+"}),(b:"+f"{virus_type}),p = shortestPath((a)-[r:contact*]-(b)) return r"
    query="\"%s\""%q
    query="CALL apoc.export.json.query("+query+",null,{"+"stream:true})YIELD data "
    print(query)
    
    fr=runquery(query)[0]['data']
    if len(fr)==0:
      return None
    fr=fr.split("\n")
    fr=min(fr, key = len)
    fr=json.loads(fr)
    fr=fr['r']
    q="match(n{id:"+f"'{user_id}'"+"}) return id(n)"
    val=runquery(q)[0]['id(n)']
    visited=set()
    
    visited.add(str(val))
    prev={}
    i=fr[0]  
    contact_time=(i['properties']['contact_times']).split("\n")[-1]
    if i['start']['id'] in visited:
      
      prev[i['end']['id']]=int(contact_time.split(":")[0])
      visited.add(i['end']['id'])

    else:
      prev[i['start']['id']]=int(contact_time.split(":")[0])
      visited.add(i['start']['id'])
    for i in fr[1:]:
      contact_time=int(((i['properties']['contact_times']).split("\n")[0]).split(":")[0])
      if i['start']['id'] in visited:
        end_id=i['end']['id']
        visited.add(i['end']['id'])
        start_id=i['start']['id']
      else:
        end_id=i['start']['id']
        visited.add(i['start']['id'])
        start_id=i['end']['id']
      if contact_time<=prev[start_id]:
        prev[end_id]=int(((i['properties']['contact_times']).split("\n")[-1]).split(":")[0])  
      else:
        source=end_id
        return source  
    return source


def five_level(user_id,virus_type,is_source):
    val=1
    s_prob="u.p_"+virus_type[-1]
    v_type="u."+virus_type
    
    q=f"match(u) where u.id='{user_id}' return labels(u)"
    fr=runquery(q)[0]['labels(u)']
    temp=":".join(fr)
    temp="u:"+temp
    if is_source:
        val=.5

    q=f"match(u) where u.id='{user_id}' remove {temp} set u:Positive:{virus_type}:Person set {s_prob}={val}"
    runquery(q)
 
    
    query="CALL apoc.export.json.query("
    q="MATCH p=({id:"+f"'{user_id}'"+"})-[r:contact*..5]-(fr) return relationships(p),length(p),nodes(p)"
    query="\"%s\""%q
    query="CALL apoc.export.json.query("+query+",null,{"+"stream:true})YIELD data "
    print(q)
    fr=runquery(query)
    fr=fr[0]['data']

    if fr:

        fr=fr.split("\n")
        fr=list(map(json.loads,fr))
        dat=[]
        visited=set()
        prev_times={}
        for i in fr:
            dat.append((i['relationships(p)'][-1],i['length(p)']))
        dat.sort(key=lambda x:x[1])    
        for i in dat:    
            if i[1]>1:
                if i[0]['start']['id'] in visited and i[0]['end']['id'] in visited:#checks if already in previous lvl
                    continue
                if i[0]['start']['id'] in prev_times :
                    id_start=i[0]['start']['id'] 
                    id_end=i[0]['end']['id']                           #finds the id of start node and end node
                elif i[0]['end']['id'] in prev_times:
                    id_start=i[0]['end']['id']
                    id_end=i[0]['start']['id'] 
                else:
                    continue
                visited.add(id_end)
                first_contact_times=i[0]['properties']['contact_times'].split("\n")
                temp=[]
                for p in first_contact_times:
                    temp.append(int(p.split(":")[0]))
                flag=0
                first_contact_times=temp
                
                for j in range(len(first_contact_times)): 
                    if first_contact_times[j]>=prev_times[id_start]:
                        contact_time=first_contact_times[j]
                        flag=1
                        break
                if flag:    
                    prob=find_probability(i,virus_type)  
                    q=f"match(u) where id(u)={id_end} return labels(u),{s_prob}"
                    q_res=runquery(q)[0]
                    
                    prob_end=q_res[s_prob]
                    if prob>prob_end:
                        prev_times[id_end]=contact_time
                        q=f"MATCH (u:Person) WHERE id(u)={id_end} SET {s_prob}={prob} set u:{virus_type}"
                        runquery(q)




              

            else:
                first_contact_times=i[0]['properties']['contact_times'].split("\n")
                id_start=i[0]['start']['id']
                id_end=i[0]['end']['id']
                visited.add(id_end)
                visited.add(id_start)
                q=f"match(u) where id(u)={id_start} return labels(u),{s_prob}"
                q_res=runquery(q)[0]
                labels_start=q_res['labels(u)']
                print(q_res,s_prob)
                prob_start=q_res[s_prob] 
                q=f"match(u) where id(u)={id_end} return labels(u),{s_prob}"
                q_res=runquery(q)[0]
                labels_end=q_res['labels(u)'] 
                prob_end=q_res[s_prob]
                
                if current_time()-int(first_contact_times[-1].split(":")[0])<14*3600 and prob_start!=prob_end:
                    prob=find_probability(i,virus_type)
                    
                    if prob_start<prob_end and prob_start<prob:
                        prev_times[id_start]=int(first_contact_times[-1].split(":")[0])
                        q=f"MATCH (u) WHERE id(u)={id_start} SET {s_prob}={prob} SET u:{virus_type}"
                        runquery(q)
                    elif prob_end<prob:
                        prev_times[id_end]=int(first_contact_times[-1].split(":")[0])
                        
                        q=f"MATCH (u) WHERE id(u)={id_end} SET {s_prob}={prob} SET u:{virus_type}"
                        runquery(q)
    return jsonify(201)
@app.route("/register",methods=['POST'])
def register_user():
    p_A=0
    p_B=0
    p_C=0 
    data_recieved =request.data
   
    data_recieved=json.loads(data_recieved.decode("utf-8"))
    age,gender=data_recieved['age'],data_recieved['gender']
    user_id = uuid.uuid4()
    
    query=f" id:'{user_id}', age: {age},gender: '{gender}',p_A: {p_A},p_C: {p_C},p_B: {p_B}"
    query="CREATE (n:Person {"+query+"})"
    session=driver.session()
    session.run(query)
    return jsonify({"user_id":user_id})


@app.route("/new_contact",methods=['POST'])
def new_contact():
    data_recieved =request.data
    data_recieved=data_recieved.decode("utf-8")
    
    data_recieved=json.loads(data_recieved)
    
    user_id,connected_ids,temperature,humidity=data_recieved['user_id'],data_recieved['connections'], data_recieved['temperature'],data_recieved['humidity']
    
    
    
    for m in connected_ids:
        duration=connected_ids[m]
        m = m.lower()
        query="MATCH (x{id:"+f"'{user_id}'"+"})-[r:contact]-(z{id:"+f"'{m}'"+"}) RETURN properties(r)"
        session=driver.session()
        fr=session.run(query)
        fr= fr.data()
        if fr:
            
            fr=fr[0]['properties(r)']['contact_times']  
            fr=fr.split("\n")
            fr.append(f"{current_time()}:{duration}")
            contact_time_list="\n".join(fr)
            q="MATCH  (:Person {id:"+f"'{user_id}'"+"})-[r:contact]-(:Person {id:"+f"'{m}'"+"}) Set r.contact_times="+f"'{contact_time_list}'"
            session=driver.session()
            session.run(q)
        else:
            contact_time_list=f"{current_time()}:{duration}"
            query=f"MATCH (a:Person), (b:Person) WHERE a.id ='{user_id}'AND b.id = '{m}' CREATE (a)-[r:contact " +"{"+f"dur:0, humidity:'{humidity}',temperature:'{temperature}',contact_times:'{contact_time_list}'"+"}]->(b)"
            session=driver.session()
            session.run(query)

    
    return jsonify(200)

@app.route("/probability",methods=['POST']) 
def check_probability():
    val=0
    virus_type=None
    data_recieved =request.data
    data_recieved=json.loads(data_recieved.decode("utf-8"))
    user_id=data_recieved['user_id']
   
    q="match(n{id:"+f"'{user_id}'"+"}) return n.p_B,n.p_A,n.p_C,labels(n)" 
    fr=runquery(q)
    virus_type={}
    if fr:
        fr=fr[0]
        p_A,p_B,p_C=int(fr['n.p_A'])*100,int(fr['n.p_B'])*100,int(fr['n.p_C'])*100
        
        for i in fr['labels(n)']:
            if i=="Positive" or i=="Person":
                continue
            if i=="v_A":
                virus_type["Virus A"]=p_A
            elif i=="v_B":
                virus_type["Virus B"]=p_B
            else:
                virus_type["Virus C"]=p_C   

    if len(virus_type)==0:
        virus_type={"No Infection": 0}
    return jsonify(virus_type)
    
@app.route("/positive",methods=['POST'])
def is_positive():
    data_recieved =request.data
    data_recieved=json.loads(data_recieved.decode("utf-8"))
    user_id,virus_type=data_recieved['user_id'],data_recieved['virus_type']# SEnd virus type as v_A, v_B or v_C
    if virus_type=="v_B":
        ret="a.p_B"
    elif virus_type=="v_A":
        ret="a.p_A" 
    else:
        ret="a.p_C"         
    query=f"MATCH (a:Person) WHERE a.id='{user_id}' Return {ret}"
    #ret="\'%s\'"%ret
    val=runquery(query)
    source=None
    if val:
        val=val[0]
        val=val[ret]
        if val<.05:
            source=findsource(user_id,virus_type)
        if source!=None:
            q=f"match (n) where id(n)={source} return n.id"
            val=runquery(q)[0]['n.id']
            five_level(val,virus_type,1) 
    return five_level(user_id,virus_type,0)  


@app.route("/police",methods=['POST'])
def police():
    d={}
    data_recieved =request.data
    data_recieved=json.loads(data_recieved.decode("utf-8")) 
    connections=data_recieved['connections']
     
    for i,j in connections.items():
        i = i.lower()
        if int(j)>-100:
            query="match(n{id:"+f"'{i}'"+"}) return n.p_A,n.p_B,n.p_C" 
            fr=runquery(query)
            if len(fr)>0:
                fr=fr[0]
                p_A,p_B,p_C=int(fr['n.p_A'])*100,int(fr['n.p_B'])*100,int(fr['n.p_C'])*100
                d[i]=[p_A,p_B,p_C]# returned probability of each virus in order A,B,C
    if len(d)==0:
        d={"No Person Nearby": 0}   

    return jsonify(d)
if __name__=='__main__':
    app.run()
