import os
from openai import OpenAI
import json
from typing import List
from chain import FusionChain, MinimalChainable
from tqdm import tqdm

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_personas(scraped_text: str) -> List[str]:
    """
    Generate personas based on scraped website content.
    
    Args:
    scraped_text (str): The scraped content of the website.
    
    Returns:
    List[str]: A list of JSON strings, each representing a persona.
    """
    context = {"website_content": scraped_text}
    
    # Define 4 initial personas with different "seed" personalities
    models = ["analytical", "creative", "practical", "enthusiastic"]
    
    print("Generating initial personas...")
    # Create a progress bar
    pbar = tqdm(total=len(models) * 4, desc="Generating personas", unit="step")
    
    # Custom callable to update progress bar
    def prompt_with_progress(model: str, prompt_text: str) -> str:
        result = call_openai(model, prompt_text)
        pbar.update(1)
        return result
    
    # Run the FusionChain to generate personas
    result = FusionChain.run(
        context=context,
        models=models,
        callable=prompt_with_progress,
        prompts=[
            # Part 1: Generate basic persona info
            """Based on the following website content, generate a basic persona including name, age, gender, ethnicity, location, occupation, income level, and education level. The persona should have a {{model}} personality type. Respond in strictly JSON format:
            {{website_content}}
            """,
            # Part 2: Generate psychographics
            """Using the basic persona information and the website content, generate psychographics including values & beliefs, challenges, needs, frustrations, goals, and behaviors. Use the following JSON as context:
            {{output[-1]}}
            Respond in strictly JSON format, adding to the existing JSON.
            """,
            # Part 3: Generate habits
            """Based on the persona developed so far and the website content, generate habits including other brands, purchases, lifestyle, interests, and media consumption. Use the following JSON as context:
            {{output[-1]}}
            Respond in strictly JSON format, adding to the existing JSON.
            """,
            # Part 4: Generate Flashmark.insights
            """Create a brief Flashmark.insights section for the persona, focusing on their decision-making process and metrics for success. Use the following JSON as context:
            {{output[-1]}}
            Respond in strictly JSON format, adding to the existing JSON.
            """,
            # # Part 5: Generate "A Day in the Life"
            # """Using all the information generated so far, create a detailed "A Day in the Life" narrative for this persona. The narrative should be at least 300 words long and showcase the persona's habits, challenges, and interactions with the product or service related to the website. Use the following JSON as context:
            # {{output[-1]}}
            # Respond with a markdown-formatted narrative.
            # """
        ],
        evaluator=evaluate_personas,
        get_model_name=lambda model: model,
    )
    
    # Close the progress bar
    pbar.close()

    print("Finalizing personas...")
    # Combine JSON and narrative for each persona
    final_personas = []
    for i, persona in enumerate(result.all_prompt_responses, 1):
        print(f"Finalizing persona {i} of {len(result.all_prompt_responses)}...")
        try:
            json_data = json.loads(persona[-2])  # Get the JSON data from the second-to-last prompt
            narrative = persona[-1]  # Get the narrative from the last prompt
            json_data["A Day in the Life"] = narrative
            final_personas.append(json.dumps(json_data, indent=2))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON for persona {i}:")
            print(f"Content: {persona[-2]}")
            print(f"Error: {str(e)}")
            # Add a placeholder for the failed persona
            # final_personas.append(json.dumps({"error": f"Failed to parse persona {i}"}, indent=2))
    
    return final_personas

def call_openai(model: str, prompt: str) -> str:
    """
    Send a prompt to the OpenAI API and get the response.
    
    Args:
    model (str): The personality type of the persona.
    prompt (str): The prompt to send to the API.
    
    Returns:
    str: The API's response.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You are creating a {model} persona based on website content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

def evaluate_personas(outputs: List[str]) -> tuple[str, List[float]]:
    """
    Evaluate the generated personas based on their relevance to the website content.
    
    Args:
    outputs (List[str]): The list of generated personas.
    
    Returns:
    tuple[str, List[float]]: The top response and a list of scores for each persona.
    """
    evaluation_prompt = f"""
    Evaluate the following personas based on how well they represent ideal users for the website. 
    Consider factors such as relevance to the product/service, potential engagement, and likelihood of conversion.
    Provide a score from 0 to 1 for each persona, where 1 is the most ideal.

    Personas:
    {outputs}

    Respond with a JSON array of scores, e.g., [0.8, 0.9, 0.7, 0.85]
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse the content as JSON
        try:
            scores = json.loads(content)
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract the scores using regex
            import re
            scores_match = re.search(r'\[([\d., ]+)\]', content)
            if scores_match:
                scores = [float(score.strip()) for score in scores_match.group(1).split(',')]
            else:
                raise ValueError("Unable to extract scores from the API response")
        
        if not isinstance(scores, list) or len(scores) != len(outputs):
            raise ValueError(f"Expected {len(outputs)} scores, but got {len(scores) if isinstance(scores, list) else 'non-list'}")
        
        top_response = outputs[scores.index(max(scores))]
        
        return top_response, scores
    except Exception as e:
        print(f"Error in evaluate_personas: {str(e)}")
        print(f"API response content: {content}")
        # Return default values in case of error
        return outputs[0], [1.0] * len(outputs)
