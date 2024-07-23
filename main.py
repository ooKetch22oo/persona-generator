import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from persona_generator import generate_personas
from neo4j_operations import Neo4jOperations

def scrape_website(url: str) -> str:
    """
    Scrape the content of a given URL.
    
    Args:
    url (str): The URL of the website to scrape.
    
    Returns:
    str: The text content of the website.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def main():
    # Load environment variables (including API keys)
    load_dotenv()
    
    # Get user input for the website URL
    url = input("Enter the website URL to generate personas from: ")
    
    # Scrape the website content
    scraped_text = scrape_website(url)
    
    # Generate personas based on the scraped content
    print("\nGenerating personas...")
    personas = generate_personas(scraped_text)
    
    # Initialize Neo4j connection
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    neo4j_ops = Neo4jOperations(neo4j_uri, neo4j_user, neo4j_password)
    
    # Output results and save to Neo4j
    for i, persona in enumerate(personas, 1):
        print(f"\n\n--- Persona {i} ---")
        print(persona)
        
        # Save persona to Neo4j
        neo4j_ops.save_persona(url, persona)
    
    print("\nPersonas have been saved to the Neo4j database.")
    
    # Generate insights
    print("\n--- Insights ---")
    print("\nCommon Interests:")
    common_interests = neo4j_ops.find_common_interests()
    for interest, count in common_interests:
        print(f"- {interest}: shared by {count} personas")
    
    print("\nChallenges for 25-34 age group:")
    challenges = neo4j_ops.find_challenges_by_age_group("25-34")
    for challenge, count in challenges:
        print(f"- {challenge}: faced by {count} personas")
    
    print("\nBrands preferred by personas valuing 'Innovation':")
    brands = neo4j_ops.find_brands_by_value("Innovation")
    for brand, count in brands:
        print(f"- {brand}: preferred by {count} personas")
    
    print("\nPersonas similar to the first persona:")
    similar_personas = neo4j_ops.find_similar_personas(personas[0]['name'])
    for persona, similarity in similar_personas:
        print(f"- {persona}: {similarity} shared attributes")
    
    # Close Neo4j connection
    neo4j_ops.close()

if __name__ == "__main__":
    main()
