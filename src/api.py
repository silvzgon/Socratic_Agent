from openai import OpenAI
from multipledispatch import dispatch
import time

model = 'gpt-4o'
api_key = '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'

def call_api(messages):
    client = OpenAI(api_key = api_key)

    response = client.chat.completions.create(
        model    = model,
        messages = messages
    )

    return response.choices[0].message.content

def run_code_interpreter(client, assistant, messages):
    thread = client.beta.threads.create(messages = messages)
    run = client.beta.threads.runs.create(
        thread_id    = thread.id,
        assistant_id = assistant.id
    )

    while (1):
        time.sleep(0.1)
        run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id    = run.id
        )
        if run.status == 'completed': break

    output = client.beta.threads.messages.list(
        thread_id = thread.id
    )
    return output.data[0].content[0].text.value

@dispatch(list, str, list)
def code_interpreter(file_paths, instructions, messages):
    client = OpenAI(api_key = api_key)
    file_id = []
    
    for file_path in file_paths:
        file = client.files.create(
            file    = open(file_path, 'rb'),
            purpose = 'assistants'
        )
        file_id.append(file.id)

    assistant = client.beta.assistants.create(
        instructions   = instructions,
        model          = model,
        tools          = [{"type": "code_interpreter"}],
        tool_resources = {"code_interpreter": {"file_ids": file_id}}
    )
    
    return run_code_interpreter(client, assistant, messages)

@dispatch(str, list)
def code_interpreter(instructions, messages):
    client = OpenAI(api_key = api_key)
    
    assistant = client.beta.assistants.create(
        instructions = instructions,
        model        = model,
        tools        = [{"type": "code_interpreter"}],
    )

    return run_code_interpreter(client, assistant, messages)