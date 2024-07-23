from neo4j import GraphDatabase
import json

class Neo4jOperations:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def save_persona(self, persona, website_url):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link_persona, persona, website_url)

    @staticmethod
    def _create_and_link_persona(tx, persona, website_url):
        persona_data = json.loads(persona)
        
        # Create Website node
        tx.run("MERGE (w:Website {url: $url})", url=website_url)

        # Create Persona node
        persona_query = """
        CREATE (p:Persona {
            name: $name,
            age: $age,
            gender: $gender,
            ethnicity: $ethnicity,
            location: $location,
            occupation: $occupation,
            income: $income,
            education: $education
        })
        WITH p
        MATCH (w:Website {url: $website_url})
        CREATE (p)-[:GENERATED_FROM]->(w)
        RETURN p
        """
        result = tx.run(persona_query, 
                        name=persona_data['name'],
                        age=persona_data['age'],
                        gender=persona_data['gender'],
                        ethnicity=persona_data['ethnicity'],
                        location=persona_data['location'],
                        occupation=persona_data['occupation'],
                        income=persona_data['income'],
                        education=persona_data['education'],
                        website_url=website_url)
        persona_node = result.single()[0]

        # Create and link psychographics
        for key, value in persona_data.get('psychographics', {}).items():
            tx.run("MATCH (p:Persona) WHERE id(p) = $persona_id "
                   "MERGE (psy:Psychographic {type: $type, value: $value}) "
                   "CREATE (p)-[:HAS_PSYCHOGRAPHIC]->(psy)",
                   persona_id=persona_node.id, type=key, value=str(value))

        # Create and link habits
        for key, value in persona_data.get('habits', {}).items():
            tx.run("MATCH (p:Persona) WHERE id(p) = $persona_id "
                   "MERGE (h:Habit {type: $type, value: $value}) "
                   "CREATE (p)-[:HAS_HABIT]->(h)",
                   persona_id=persona_node.id, type=key, value=str(value))

        # Create and link brands
        for brand in persona_data.get('habits', {}).get('preferred_brands', []):
            tx.run("MATCH (p:Persona) WHERE id(p) = $persona_id "
                   "MERGE (b:Brand {name: $brand}) "
                   "CREATE (p)-[:PREFERS]->(b)",
                   persona_id=persona_node.id, brand=brand)

        # Create and link interests
        for interest in persona_data.get('habits', {}).get('interests', []):
            tx.run("MATCH (p:Persona) WHERE id(p) = $persona_id "
                   "MERGE (i:Interest {name: $interest}) "
                   "CREATE (p)-[:INTERESTED_IN]->(i)",
                   persona_id=persona_node.id, interest=interest)

        # Create and link insights
        for key, value in persona_data.get('Flashmark.insights', {}).items():
            tx.run("MATCH (p:Persona) WHERE id(p) = $persona_id "
                   "CREATE (p)-[:HAS_INSIGHT]->(:Insight {type: $type, value: $value})",
                   persona_id=persona_node.id, type=key, value=str(value))

    def find_common_traits(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_common_traits)

    @staticmethod
    def _get_common_traits(tx):
        query = """
        MATCH (p:Persona)-[:HAS_PSYCHOGRAPHIC]->(psy:Psychographic)
        WITH psy.type AS trait, psy.value AS value, COUNT(*) AS count
        WHERE count > 1
        RETURN trait, value, count
        ORDER BY count DESC
        LIMIT 10
        """
        result = tx.run(query)
        return [{"trait": record["trait"], "value": record["value"], "count": record["count"]} 
                for record in result]

    def find_brand_insights(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_brand_insights)

    @staticmethod
    def _get_brand_insights(tx):
        query = """
        MATCH (p:Persona)-[:PREFERS]->(b:Brand)
        WITH b.name AS brand, COUNT(*) AS popularity,
             COLLECT(DISTINCT p.age) AS ages,
             COLLECT(DISTINCT p.gender) AS genders,
             COLLECT(DISTINCT p.occupation) AS occupations
        RETURN brand, popularity, ages, genders, occupations
        ORDER BY popularity DESC
        LIMIT 5
        """
        result = tx.run(query)
        return [{"brand": record["brand"], 
                 "popularity": record["popularity"],
                 "age_range": f"{min(record['ages'])}-{max(record['ages'])}",
                 "genders": record["genders"],
                 "occupations": record["occupations"]} 
                for record in result]

    def find_interest_demographics(self):
        with self.driver.session() as session:
            return session.read_transaction(self._get_interest_demographics)

    @staticmethod
    def _get_interest_demographics(tx):
        query = """
        MATCH (p:Persona)-[:INTERESTED_IN]->(i:Interest)
        WITH i.name AS interest, COUNT(*) AS popularity,
             AVG(p.age) AS avg_age,
             COLLECT(DISTINCT p.gender) AS genders,
             COLLECT(DISTINCT p.occupation) AS occupations
        RETURN interest, popularity, avg_age, genders, occupations
        ORDER BY popularity DESC
        LIMIT 5
        """
        result = tx.run(query)
        return [{"interest": record["interest"], 
                 "popularity": record["popularity"],
                 "average_age": round(record["avg_age"], 1),
                 "genders": record["genders"],
                 "occupations": record["occupations"]} 
                for record in result]
