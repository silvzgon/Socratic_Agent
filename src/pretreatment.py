import json
import uuid
import prompts
import api
import log

step_file_path = './step/step.json'

def extract_content(string):
    first_open = string.find('[')
    last_close = string.rfind(']')
    
    if first_open != -1 and last_close != -1 and first_open < last_close:
        return string[first_open : last_close + 1]
    else:
        return None

def check_structure(string):
    try:
        data = json.loads(string)
    except Exception:
        return False

    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                if ("question"    in item and isinstance(item["question"]    , str ) and
                    "answer"      in item and isinstance(item["answer"]      , str ) and
                    "description" in item and isinstance(item["description"] , list) and
                    all(isinstance(desc, str) for desc in item["description"])):
                    continue
                else:
                    return False
            else:
                return False
        return True
    else:
        return False

def solve_problem(instructions, messages, file_path, type):
    if type == 1:
        try:
            output = api.code_interpreter(instructions, messages)
            return True, output
        except Exception as e:
            log.logger.error(f'Error in solve_problem. {{{e}}}')
            return False, None

    if type == 2:
        messages[-1]["content"] += '\n给出的文件中是对于题目的一些补充。'
        try:
            output = api.code_interpreter([file_path], instructions, messages)
            return True, output
        except Exception as e:
            log.logger.error(f'Error in solve_problem. {{{e}}}')
            return False, None

def standardize_steps(output):
    messages = [{"role": "system", "content": prompts.standardize_steps},
                {"role": "user"  , "content": output}]
    while not check_structure(output):
        try:
            output = api.call_api(messages)
            output = extract_content(output)
        except Exception as e:
            log.logger.error(f'Error in standardize_steps. {{{e}}}')
            return False, None, None

    data = json.loads(output)
    random = str(uuid.uuid4())
    file_name = 'step/step-' + random + '.json'
    with open(file_name, "w", encoding = "utf-8") as file:
        json.dump(data, file, indent = 4, ensure_ascii = False)
    return True, output, random

def check_steps(messages, file_path, type):
    instructions = '你是一名个人助手，请你根据历史记录，改进解题步骤，使其【通过】。如果需要，请写代码并执行来保证解题步骤的正确性。'
    output = None

    if type == 1:
        while not output or (not output.startswith('【通过】') and not output.startswith('【不通过】')):
            try:
                output = api.code_interpreter(instructions, messages)
            except Exception as e:
                log.logger.error(f'Error in check_steps. {{{e}}}')
                return False, None

    if type == 2:
        messages[-1]["content"] += '\n给出的文件中是对于题目的一些补充。'
        while not output or (not output.startswith('【通过】') and not output.startswith('【不通过】')):
            try:
                output = api.code_interpreter([file_path], instructions, messages)
            except Exception as e:
                log.logger.error(f'Error in check_steps. {{{e}}}')
                return False, None
            
    if output.startswith('【通过】'):
        return True, None
    if output.startswith('【不通过】'):
        return False, output

def get_steps(user_input, file_path, type):
    messages = [{"role": "user", "content": user_input}]
    complete, output = solve_problem(prompts.solve_problem, messages, file_path, type)
    if not complete:
        return False, None
    
    complete, output, random = standardize_steps(output)
    if not complete:
        return False, None
    complete = False

    messages = [{"role": "user"     , "content": prompts.solve_problem + user_input},
                {"role": "assistant", "content": output},
                {"role": "user"     , "content": prompts.check_steps + user_input}]
    while not complete:
        complete, output = check_steps(messages, file_path, type)
        if not complete:
            if not output:
                return False, None
            else:
                output = extract_content(output)
                if check_structure(output):
                    file_name = 'step/step-' + random + '.json'
                    with open(file_name, "w", encoding = "utf-8") as file:
                        file.write(output)
                    messages.append({"role": "assistant", "content": output})
                    messages.append({"role": "user",      "content": "请你结合历史对话，继续对上一轮中的解题步骤进行检查。如果检查无误，请直接通过。"})
                    
    return True, random