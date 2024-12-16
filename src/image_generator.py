import os
import replicate

def generate_image(replicate_api_token, prompt, output_dir, filename):
    """
    Generate an image using the Replicate API and save it locally.
    """
    os.environ["REPLICATE_API_TOKEN"] = replicate_api_token
    
    # Use the Replicate model
    input_data = {
        "prompt": prompt
    }
    outputs = replicate.run("black-forest-labs/flux-schnell", input=input_data)

    return outputs
