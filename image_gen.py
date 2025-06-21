import base64
from openai import OpenAI
def generate_image(client:OpenAI,prompt:str,model:str="gpt-image-1",n=1,size="1024x1024",response_format="b64_json",output_filename="output.png"):
    print(f"Generating {n} {size} image(s) for: {prompt}")
    img = client.images.generate(
        model=model,
        prompt=prompt,
        n=n,
        size=size
    )

    if response_format == "b64_json":
        print(f"Saving image to {output_filename}")
        save_base64_image(img.data[0].b64_json, output_filename)
    else:
        return "TODO"

def save_base64_image(b64_string, output_filename):
    image_bytes = base64.b64decode(b64_string)
    with open(output_filename, "wb") as f:
        f.write(image_bytes)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_image(client,prompt,image_path,model="gpt-4.1"):
    
    response = client.responses.create( 
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    { "type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{encode_image(image_path)}",
                    },
                ],
            }
        ],
    )

    return response.output_text

def edit_image(client,prompt,image_paths,output_filename="output.png",model="gpt-image-1"):
    if len(image_paths) > 1:
        image_files = [open(path, "rb") for path in image_paths]
        print(image_files)
    else: 
        image_files = open(str(image_paths[0]),"rb")
    
    try:
        result = client.images.edit(
            model=model,
            image= image_files,
            prompt=prompt
        )

        
        
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)

        with open(output_filename, "wb") as f:
            f.write(image_bytes)
    finally:
        for f in image_files:
            f.close()

