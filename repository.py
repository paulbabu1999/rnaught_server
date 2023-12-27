# repositories.py
from neo4j import GraphDatabase
from datetime import datetime
import json
from utils import findsource, five_level

class UserRepository:
    def __init__(self, driver):
        self.driver = driver

    def register_user(self, data):
        user_id = data['user_id']
        age, gender = data['age'], data['gender']

        query = f"CREATE (n:Person {{id:'{user_id}', age: {age}, gender: '{gender}'}})"
        
        with self.driver.session() as session:
            session.run(query)

class ContactRepository:
    def __init__(self, driver):
        self.driver = driver

    def new_contact(self, data):
        user_id = data['user_id']
        connected_ids = data['connections']
        temperature, humidity = data['temperature'], data['humidity']

        with self.driver.session() as session:
            for m, duration in connected_ids.items():
                m = m.lower()
                query = f"MATCH (x {{id:'{user_id}'}})-[r:contact]-(z {{id:'{m}'}}) RETURN properties(r)"
                fr = session.run(query).data()

                if fr:
                    fr = fr[0]['properties(r)']['contact_times']
                    fr = fr.split("\n")
                    fr.append(f"{current_time()}:{duration}")
                    contact_time_list = "\n".join(fr)
                    q = f"MATCH  (:Person {{id:'{user_id}'}})-[r:contact]-(:Person {{id:'{m}'}}) SET r.contact_times='{contact_time_list}'"
                    session.run(q)
                else:
                    contact_time_list = f"{current_time()}:{duration}"
                    query = f"MATCH (a:Person), (b:Person) WHERE a.id ='{user_id}' AND b.id = '{m}' CREATE (a)-[r:contact {{dur:0, humidity:'{humidity}', temperature:'{temperature}', contact_times:'{contact_time_list}'}}]->(b)"
                    session.run(query)

    def current_time(self):
        now = datetime.now()
        dt_string = now.strftime("%d %m %Y %H %M %S")
        dt_string = list(map(int, dt_string.split(" ")))
        ltime = dt_string[-2]+dt_string[-3]*60 + dt_string[0] * 3600 + dt_string[1]*3600*30 + dt_string[2]*365*3600
        return ltime

class ProbabilityRepository:
    def __init__(self, driver):
        self.driver = driver

    def check_probability(self, data):
        user_id = data['user_id']

        query = f"MATCH(n {{id:'{user_id}'}}) RETURN n.p_B, n.p_A, n.p_C, labels(n)"
        with self.driver.session() as session:
            fr = session.run(query).data()

        virus_type = {}
        if fr:
            fr = fr[0]
            p_A, p_B, p_C = int(fr['n.p_A']) * 100, int(fr['n.p_B']) * 100, int(fr['n.p_C']) * 100

            for label in fr['labels(n)']:
                if label == "Positive" or label == "Person":
                    continue
                if label == "v_A":
                    virus_type["Virus A"] = p_A
                elif label == "v_B":
                    virus_type["Virus B"] = p_B
                else:
                    virus_type["Virus C"] = p_C

        if not virus_type:
            virus_type = {"No Infection": 0}

        return virus_type
    
    def is_positive(self, data):
        user_id, virus_type = data['user_id'], data['virus_type']
        if virus_type == "v_B":
            ret = "a.p_B"
        elif virus_type == "v_A":
            ret = "a.p_A"
        else:
            ret = "a.p_C"
        query = f"MATCH (a:Person) WHERE a.id='{user_id}' RETURN {ret}"
        with self.driver.session() as session:
            val = session.run(query).data()

        source = None
        if val:
            val = val[0]
            val = val[ret]
            if val < 0.05:
                source = self.find_source(user_id, virus_type, session)
            if source is not None:
                q = f"MATCH (n) WHERE id(n)={source} RETURN n.id"
                val = session.run(q).data()[0]['n.id']
                self.five_level(val, virus_type, 1, session)
        
        return self.five_level(user_id, virus_type, 0, session)

    def find_source(self, user_id, virus_type):
        return findsource(self.runquery, user_id, virus_type)

    def five_level(self, user_id, virus_type, is_source):
        return five_level(self.runquery, self.current_time, self.find_probability, user_id, virus_type, is_source)


    def runquery(self, query):
        with self.driver.session() as session:
            fr = session.run(query).data()
        return fr

    def current_time(self):
        now = datetime.now()
        dt_string = now.strftime("%d %m %Y %H %M %S")
        dt_string = list(map(int, dt_string.split(" ")))
        ltime = dt_string[-2]+dt_string[-3]*60 + dt_string[0] * 3600 + dt_string[1]*3600*30 + dt_string[2]*365*3600
        return ltime

    def find_probability(self, a, virus_type):
        return 0.92/int(a[1])

class PoliceRepository:
    def __init__(self, driver):
        self.driver = driver

    def police(self, data):
        connections = data['connections']
        d = {}

        with self.driver.session() as session:
            for i, j in connections.items():
                i = i.lower()
                if int(j) > -100:
                    query = f"MATCH(n {{id:'{i}'}}) RETURN n.p_A, n.p_B, n.p_C"
                    fr = session.run(query).data()
                    if fr:
                        fr = fr[0]
                        p_A, p_B, p_C = int(fr['n.p_A']) * 100, int(fr['n.p_B']) * 100, int(fr['n.p_C']) * 100
                        d[i] = [p_A, p_B, p_C]

        if not d:
            d = {"No Person Nearby": 0}

        return d
