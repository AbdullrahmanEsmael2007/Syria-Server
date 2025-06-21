
def text_generation(client,input, model="gpt-4o-mini", instructions="You are a helpful assistant"):

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=input
    )

    return (response.output_text)