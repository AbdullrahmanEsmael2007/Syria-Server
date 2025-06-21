from text_gen import text_generation
from image_gen import analyze_image, generate_image, edit_image
import streamlit as st
from openai import OpenAI
import os

current_folder = os.getcwd() 
option = None
api_key = None

with st.sidebar:
    api_key = st.text_input("Enter OpenAI API key") or None
    client = OpenAI(api_key=api_key)
    st.success(f"API Key: {client.api_key}")
    option = st.selectbox("Select Tool",("Image Tools","Prompt Tools","Text Generation","Code Developer","Searching"))
    entered = True
        

def generate_image_page():
    st.title("Image Generation")
    prompt = st.text_input("Enter prompt")
    output_filename = st.text_input("Enter filename")+".png" or "output.png"
    model = st.selectbox("Model",("gpt-image-1"))

    generate_button = st.button("Generate")
    if generate_button and prompt:
        generate_image(client,prompt, model=model, output_filename=output_filename)
        st.image(output_filename, caption=prompt)
        print(os.path.join(current_folder, output_filename))
        with open(os.path.join(current_folder, output_filename), "rb") as f:
            st.download_button("Download", f.read(), output_filename, mime="image/png")
    elif not prompt and generate_button:
        st.error("Add a prompt")

def analyze_image_page():
    st.title("Image Analyzation")
    uploaded_files = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"],accept_multiple_files=True)
    col1,col2 = st.columns(2)
    with col1:
        prompt = st.text_input("Enter prompt") or "Analyse this image"
    with col2:
        model = st.selectbox("Model",("gpt-4.1-mini","gpt-4o-mini"))

    analyse_button = st.button("Analyse Image")
    if analyse_button and prompt and uploaded_files:
        for file in uploaded_files:
                input_path = f"uploaded_{file.name}"
                with open(input_path, "wb") as f:
                    f.write(file.read())
                analysis = analyze_image(client, prompt, image_path=input_path)
                st.write(f"Analysis for {file.name}:", analysis)
    elif not prompt and analyse_button and not uploaded_files:
        st.error("Add a prompt or files ASAP.")

def edit_image_page():
    st.title("Image Editor")
    uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    col1,col2 = st.columns(2)
    with col1:
        prompt = st.text_input("Enter prompt")
    with col2:
        model = st.selectbox("Model",("gpt-image-1"))
    edit_button = st.button("Edit All Images")
    if uploaded_files and edit_button and prompt:
        image_paths = []
        for file in uploaded_files:
            input_path = f"uploaded_{file.name}"
            with open(input_path, "wb") as f:
                f.write(file.read())
            image_paths.append(input_path)

        output_filename = "edited_result.png"
        edit_image(client, prompt, image_paths=image_paths,model=model, output_filename=output_filename)
        st.image(output_filename, caption="Edited Result")
        with open(output_filename, "rb") as f:
            st.download_button("Download Edited Image", f.read(), output_filename, mime="image/png")
    elif edit_button and not prompt or not uploaded_files:
        st.error("Add a prompt or files, you fool.")

def prompt_rewriter_page():
    st.title("Prompt Rewriter")
    prompt = st.text_area("Enter the prompt...")
    style_instruction = st.text_input("How should the new prompt sound like?") or "more detailed"

    input_prompt = f"""
    You are a tool designed for prompt transformation. Your primary objective is to take a prompt and modify it to align with a distinct style or tone. Incase of the prompt being used to generate an image, make sure to describe camera properties like lens mm, blur, lightning, etc    

    Please proceed to revise the prompt below:

    “{prompt}”

    Ensure that the revised prompt is: {style_instruction}.

    Return only the newly crafted prompt without any quotation
    """
    
    rewrite_prompt = st.button("Rewrite prompt")

    if rewrite_prompt and prompt:
        response = text_generation(client,input_prompt,instructions="You are a prompt rewriting tool.")
        st.write(response)
    elif rewrite_prompt and not prompt:
        st.error("Missing inputs")

def prompt_extractor_page():
    st.title("Prompt Extractor")
    mode = st.radio("Choose input type", ("Image", "Text"))
    extracted_prompt = None

    if mode == "Image":
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        if uploaded_file:
            input_path = f"uploaded_{uploaded_file.name}"
            with open(input_path, "wb") as f:
                f.write(uploaded_file.read())
            extract_button = st.button("Extract Prompt from Image")
            if extract_button:
                extracted_prompt = analyze_image(client, "Extract the most detailed prompt that could generate this image.", image_path=input_path)
    else:
        text_input = st.text_area("Paste the generated text here...")
        extract_button = st.button("Extract Prompt from Text")
        if extract_button and text_input:
            extraction_instruction = "Extract the original prompt or intent that could have generated the following text, focusing on its style and flow. Return only the prompt."
            extracted_prompt = text_generation(client, text_input, instructions=extraction_instruction)

    if extracted_prompt:
        st.success("Extracted Prompt:")
        st.code(extracted_prompt, language="markdown")
        st.button("Copy to clipboard", on_click=st.experimental_set_query_params, args=(dict(prompt=extracted_prompt),))
        
prompt = None
uploaded_file = None

if option == "Image Tools":
    image_option = st.sidebar.selectbox("Select Image Tool",("Generate Image","Analyse Image", "Edit Image"))
    if image_option == "Generate Image":
        generate_image_page()
    elif image_option == "Analyse Image":
        analyze_image_page()
    elif image_option == "Edit Image":
        edit_image_page()

elif option == "Prompt Tools":
    prompt_option = st.sidebar.selectbox("Select Prompt Tool",("Prompt Extractor","Prompt Rewriter"))

    if prompt_option == "Prompt Extractor":
        prompt_extractor_page()
    elif prompt_option == "Prompt Rewriter":
        prompt_rewriter_page()


elif option == "Text Generation":
    st.title("Text Generation")
    prompt = st.text_area("Enter your prompt...")

    # Additional settings
    st.subheader("Generation Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        length = st.slider("Length (max tokens)", min_value=16, max_value=2048, value=256, step=16)
    with col2:
        style = st.selectbox("Style", ["Default", "Formal", "Casual", "Creative", "Technical"])
    with col3:
        language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Chinese", "Other"])

    generate_button = st.button("Generate Text")
    if generate_button and prompt:
    # Compose instructions based on settings
        instructions = f"Generate a {style.lower()} response in {language}. Limit the output to about {length} tokens."
        response = text_generation(
            client,
            prompt,
            instructions=instructions
        )
        st.write(response)
    elif generate_button and not prompt:
        st.error("Please enter a prompt.")

elif option == "Code Developer":
    st.title("Code Developer")
    prompt = st.text_area("Describe the code you want to generate...")

    # Additional code generation settings
    st.subheader("Code Generation Settings")
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("Programming Language", ["Python", "JavaScript", "Java", "C++", "Go", "Other"])
    with col2:
        complexity = st.selectbox("Complexity", ["Simple", "Intermediate", "Advanced"])

    generate_code_button = st.button("Generate Code")
    if generate_code_button and prompt:
        instructions = f"Write a {complexity.lower()} {language} code based on the following description. Return only the code."
        code_result = text_generation(client, prompt, instructions=instructions)
        st.code(code_result, language=language.lower())
    elif generate_code_button and not prompt:
        st.error("Please describe the code you want to generate.")

elif option == "Searching":
    st.title("Web Search")
    search_query = st.text_input("Enter your search query...")
    search_button = st.button("Search")
    if search_button and search_query:
        try:
            response = client.responses.create(
                model="gpt-4.1",
                tools=[{"type": "web_search_preview"}],
                input=search_query
            )
            st.write(response.output_text)
        except Exception as e:
            st.error(f"Error: {e}")
    elif search_button and not search_query:
        st.error("Please enter a search query.")













