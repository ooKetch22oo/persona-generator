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
    
    # Save personas to Neo4j
    print("\nSaving personas to Neo4j...")
    for persona in personas:
        neo4j_ops.save_persona(persona, url)
    
    # Find common traits
    common_traits = neo4j_ops.find_common_traits()
    
    # Find brand insights
    brand_insights = neo4j_ops.find_brand_insights()
    
    # Find interest demographics
    interest_demographics = neo4j_ops.find_interest_demographics()
    
    # Output the generated personas
    print("\nGeneration complete. Displaying personas:")
    for i, persona in enumerate(personas, 1):
        print(f"\n\n--- Persona {i} ---")
        print(persona)
    
    # Output common traits
    print("\nCommon traits across personas:")
    for trait in common_traits:
        print(f"{trait['trait']}: {trait['value']} (Count: {trait['count']})")
    
    # Output brand insights
    print("\nBrand insights:")
    for insight in brand_insights:
        print(f"Brand: {insight['brand']}")
        print(f"  Popularity: {insight['popularity']}")
        print(f"  Age Range: {insight['age_range']}")
        print(f"  Genders: {', '.join(insight['genders'])}")
        print(f"  Occupations: {', '.join(insight['occupations'])}")
    
    # Output interest demographics
    print("\nInterest demographics:")
    for demo in interest_demographics:
        print(f"Interest: {demo['interest']}")
        print(f"  Popularity: {demo['popularity']}")
        print(f"  Average Age: {demo['average_age']}")
        print(f"  Genders: {', '.join(demo['genders'])}")
        print(f"  Occupations: {', '.join(demo['occupations'])}")
    
    # Close Neo4j connection
    neo4j_ops.close()

if __name__ == "__main__":
    main()
