import openai

openai.api_key = "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"

def return_response(given_prompt):
    given_prompt += "Time Complexity:"

    response = openai.Completion.create(
        engine="davinci-codex",
        prompt= given_prompt,
        temperature=0,
        max_tokens=64,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    #print(response.choices[0].text)
    return response.choices[0].text