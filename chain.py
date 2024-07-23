from typing import List, Dict, Callable, Any, Union
from pydantic import BaseModel

# Define the structure of the FusionChain result
class FusionChainResult(BaseModel):
    top_response: Union[str, Dict[str, Any]]  # The best response from all models
    all_prompt_responses: List[List[Any]]  # All responses from all models
    all_context_filled_prompts: List[List[str]]  # All prompts with context filled in
    performance_scores: List[float]  # Performance scores for each model
    used_model_names: List[str]  # Names of all models used

class FusionChain:
    @staticmethod
    def run(
        context: Dict[str, Any],  # Initial context for prompts
        models: List[Any],  # List of models to use
        callable: Callable,  # Function to call models
        prompts: List[str],  # List of prompts to use
        evaluator: Callable[[List[str]], tuple[str, List[float]]],  # Function to evaluate outputs
        get_model_name: Callable[[Any], str],  # Function to get model names
    ) -> FusionChainResult:
        all_outputs = []
        all_context_filled_prompts = []

        # Run each model through the MinimalChainable
        for model in models:
            outputs, context_filled_prompts = MinimalChainable.run(
                context, model, callable, prompts
            )
            all_outputs.append(outputs)
            all_context_filled_prompts.append(context_filled_prompts)

        # Evaluate the last output of each model
        last_outputs = [outputs[-1] for outputs in all_outputs]
        top_response, performance_scores = evaluator(last_outputs)

        # Get the names of all models used
        model_names = [get_model_name(model) for model in models]

        # Return the result in the defined structure
        return FusionChainResult(
            top_response=top_response,
            all_prompt_responses=all_outputs,
            all_context_filled_prompts=all_context_filled_prompts,
            performance_scores=performance_scores,
            used_model_names=model_names,
        )

class MinimalChainable:
    @staticmethod
    def run(
        context: Dict[str, Any], model: Any, callable: Callable, prompts: List[str]
    ) -> tuple[List[Any], List[str]]:
        output = []
        context_filled_prompts = []

        for prompt in prompts:
            # Replace context placeholders in the prompt
            for key, value in context.items():
                prompt = prompt.replace("{{" + key + "}}", str(value))

            # Replace output placeholders in the prompt
            for i, prev_output in enumerate(output):
                if isinstance(prev_output, dict):
                    # Replace the entire output dict
                    prompt = prompt.replace(f"{{{{output[-{len(output)-i}]}}}}", str(prev_output))
                    # Replace individual keys from the output dict
                    for key, value in prev_output.items():
                        prompt = prompt.replace(f"{{{{output[-{len(output)-i}].{key}}}}}", str(value))
                else:
                    # Replace the entire output if it's not a dict
                    prompt = prompt.replace(f"{{{{output[-{len(output)-i}]}}}}", str(prev_output))

            context_filled_prompts.append(prompt)
            # Call the model with the filled prompt
            result = callable(model, prompt)
            output.append(result)

        return output, context_filled_prompts
