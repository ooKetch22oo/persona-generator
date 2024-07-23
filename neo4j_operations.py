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
        # Create Website node if it doesn't exist
        tx.run("MERGE (w:Website {url: $url})", url=website_url)

        # Create Persona node
        persona = json.loads(persona_data)
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
        """
        tx.run(create_persona_query, **persona)

        # Create Psychographics node and link to Persona
        create_psychographics_query = """
        MATCH (p:Persona {name: $name})
        CREATE (psy:Psychographics {
            values_and_beliefs: $values_and_beliefs,
            challenges: $challenges,
            needs: $needs,
            frustrations: $frustrations,
            goals: $goals,
            behaviors: $behaviors
        })
        CREATE (p)-[:HAS_PSYCHOGRAPHICS]->(psy)
        """
        tx.run(create_psychographics_query, **persona)

        # Create Habits node and link to Persona
        create_habits_query = """
        MATCH (p:Persona {name: $name})
        CREATE (h:Habits {
            other_brands: $other_brands,
            purchases: $purchases,
            lifestyle: $lifestyle,
            interests: $interests,
            media_consumption: $media_consumption
        })
        CREATE (p)-[:HAS_HABITS]->(h)
        """
        tx.run(create_habits_query, **persona)

        # Create Flashmark.insights node and link to Persona
        create_insights_query = """
        MATCH (p:Persona {name: $name})
        CREATE (i:Insights {content: $flashmark_insights})
        CREATE (p)-[:HAS_INSIGHTS]->(i)
        """
        tx.run(create_insights_query, **persona)

        # Create DayInLife node and link to Persona
        create_day_in_life_query = """
        MATCH (p:Persona {name: $name})
        CREATE (d:DayInLife {content: $day_in_life})
        CREATE (p)-[:HAS_DAY_IN_LIFE]->(d)
        """
        tx.run(create_day_in_life_query, **persona)

        # Link Persona to Website
        tx.run("""
        MATCH (p:Persona {name: $name})
        MATCH (w:Website {url: $url})
        CREATE (p)-[:GENERATED_FOR]->(w)
        """, name=persona['name'], url=website_url)

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
