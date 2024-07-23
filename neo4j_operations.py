from neo4j import GraphDatabase
import json

class Neo4jOperations:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def save_persona(self, website_url, persona_data):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link_persona, website_url, persona_data)

    @staticmethod
    def _create_and_link_persona(tx, website_url, persona_data):
        persona = json.loads(persona_data)

        # Create Website node
        tx.run("MERGE (w:Website {url: $url})", url=website_url)

        # Create Persona node
        create_persona_query = """
        CREATE (p:Persona {
            name: $name,
            age: $age,
            gender: $gender,
            ethnicity: $ethnicity,
            location: $location,
            occupation: $occupation,
            income_level: $income_level,
            education_level: $education_level
        })
        WITH p
        MATCH (w:Website {url: $website_url})
        CREATE (p)-[:GENERATED_FOR]->(w)
        RETURN p
        """
        result = tx.run(create_persona_query, website_url=website_url, **persona)
        persona_node = result.single()['p']

        # Create and link demographic nodes
        tx.run("""
        MATCH (p:Persona {name: $name})
        MERGE (a:AgeGroup {group: $age_group})
        MERGE (g:Gender {type: $gender})
        MERGE (e:Ethnicity {type: $ethnicity})
        MERGE (l:Location {name: $location})
        MERGE (o:Occupation {title: $occupation})
        MERGE (i:IncomeLevel {level: $income_level})
        MERGE (ed:EducationLevel {level: $education_level})
        CREATE (p)-[:IN_AGE_GROUP]->(a)
        CREATE (p)-[:HAS_GENDER]->(g)
        CREATE (p)-[:HAS_ETHNICITY]->(e)
        CREATE (p)-[:LIVES_IN]->(l)
        CREATE (p)-[:WORKS_AS]->(o)
        CREATE (p)-[:HAS_INCOME]->(i)
        CREATE (p)-[:HAS_EDUCATION]->(ed)
        """, name=persona['name'], 
        age_group=get_age_group(persona['age']),
        **persona)

        # Create and link psychographic nodes
        for value in persona['values_and_beliefs']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (v:Value {name: $value})
            CREATE (p)-[:VALUES]->(v)
            """, name=persona['name'], value=value)

        for challenge in persona['challenges']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (c:Challenge {name: $challenge})
            CREATE (p)-[:FACES]->(c)
            """, name=persona['name'], challenge=challenge)

        for need in persona['needs']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (n:Need {name: $need})
            CREATE (p)-[:NEEDS]->(n)
            """, name=persona['name'], need=need)

        for frustration in persona['frustrations']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (f:Frustration {name: $frustration})
            CREATE (p)-[:FRUSTRATED_BY]->(f)
            """, name=persona['name'], frustration=frustration)

        for goal in persona['goals']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (g:Goal {name: $goal})
            CREATE (p)-[:AIMS_FOR]->(g)
            """, name=persona['name'], goal=goal)

        for behavior in persona['behaviors']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (b:Behavior {name: $behavior})
            CREATE (p)-[:EXHIBITS]->(b)
            """, name=persona['name'], behavior=behavior)

        # Create and link habit nodes
        for brand in persona['other_brands']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (b:Brand {name: $brand})
            CREATE (p)-[:PREFERS]->(b)
            """, name=persona['name'], brand=brand)

        for purchase in persona['purchases']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (pur:Purchase {item: $purchase})
            CREATE (p)-[:BUYS]->(pur)
            """, name=persona['name'], purchase=purchase)

        for lifestyle in persona['lifestyle']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (l:Lifestyle {aspect: $lifestyle})
            CREATE (p)-[:HAS_LIFESTYLE]->(l)
            """, name=persona['name'], lifestyle=lifestyle)

        for interest in persona['interests']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (i:Interest {name: $interest})
            CREATE (p)-[:INTERESTED_IN]->(i)
            """, name=persona['name'], interest=interest)

        for media in persona['media_consumption']:
            tx.run("""
            MATCH (p:Persona {name: $name})
            MERGE (m:Media {type: $media})
            CREATE (p)-[:CONSUMES]->(m)
            """, name=persona['name'], media=media)

        # Create Flashmark.insights node and link to Persona
        tx.run("""
        MATCH (p:Persona {name: $name})
        CREATE (i:Insights {content: $flashmark_insights})
        CREATE (p)-[:HAS_INSIGHTS]->(i)
        """, name=persona['name'], flashmark_insights=persona['flashmark_insights'])

        # Create DayInLife node and link to Persona
        tx.run("""
        MATCH (p:Persona {name: $name})
        CREATE (d:DayInLife {content: $day_in_life})
        CREATE (p)-[:HAS_DAY_IN_LIFE]->(d)
        """, name=persona['name'], day_in_life=persona['A Day in the Life'])
        # Link Persona to Website
        tx.run("""
        MATCH (p:Persona {name: $name})
        MATCH (w:Website {url: $url})
        CREATE (p)-[:GENERATED_FOR]->(w)
        """, name=persona['name'], url=website_url)


    def find_common_interests(self, min_count=2):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (p:Persona)-[:INTERESTED_IN]->(i:Interest)
            WITH i, COUNT(p) as persona_count
            WHERE persona_count >= $min_count
            RETURN i.name AS interest, persona_count
            ORDER BY persona_count DESC
            """, min_count=min_count)
            return [(record["interest"], record["persona_count"]) for record in result]

    def find_challenges_by_age_group(self, age_group):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (p:Persona)-[:IN_AGE_GROUP]->(:AgeGroup {group: $age_group})
            MATCH (p)-[:FACES]->(c:Challenge)
            RETURN c.name AS challenge, COUNT(p) as count
            ORDER BY count DESC
            """, age_group=age_group)
            return [(record["challenge"], record["count"]) for record in result]

    def find_brands_by_value(self, value):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (p:Persona)-[:VALUES]->(:Value {name: $value})
            MATCH (p)-[:PREFERS]->(b:Brand)
            RETURN b.name AS brand, COUNT(p) as count
            ORDER BY count DESC
            """, value=value)
            return [(record["brand"], record["count"]) for record in result]

    def find_similar_personas(self, persona_name, min_similarity=3):
        with self.driver.session() as session:
            result = session.run("""
            MATCH (p1:Persona {name: $persona_name})-[r]->(node)<-[r2]-(p2:Persona)
            WHERE TYPE(r) = TYPE(r2)
            WITH p2, COUNT(DISTINCT TYPE(r)) AS similarity
            WHERE similarity >= $min_similarity
            RETURN p2.name AS similar_persona, similarity
            ORDER BY similarity DESC
            """, persona_name=persona_name, min_similarity=min_similarity)
            return [(record["similar_persona"], record["similarity"]) for record in result]

def get_age_group(age):
    if age < 18:
        return "Under 18"
    elif 18 <= age < 25:
        return "18-24"
    elif 25 <= age < 35:
        return "25-34"
    elif 35 <= age < 45:
        return "35-44"
    elif 45 <= age < 55:
        return "45-54"
    elif 55 <= age < 65:
        return "55-64"
    else:
        return "65+"
