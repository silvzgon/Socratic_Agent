import pretreatment
import api
import prompts
import log
import re

def get_dialogue(dialogue, messages):
    for message in messages:
        if message["role"] == "user":
            dialogue += ('#学生：' + message["content"] + '\n')
        if message["role"] == "assistant":
            dialogue += ('#老师：' + message["content"] + '\n')
    return dialogue

def call_teacher(user_input, file_path, type, random):
    file_name = 'step/step-' + random + '.json'
    with open(file_name, "r", encoding = "utf-8") as file:
        steps = file.read()

    messages = [{"role": "system", "content": prompts.teacher},
                {"role": "user"  , "content": '#题目：\n' + user_input + '\n#步骤：\n' + steps}]

    try:
        if type == 1:
            output = api.call_api(messages)
        if type == 2:
            instructions = messages[0]["content"]
            messages = messages[0:]
            messages[0]["content"] += '\n给出的文件中是对于题目的一些补充。'
            output = api.code_interpreter([file_path], instructions, messages)
        messages.append({"role": "assistant", "content": output})
    except Exception as e:
        log.logger.error(f'Error in call_teacher. {{{e}}}')
        return False, None

    return True, messages

def call_switch(messages, file_path, type):
    messages = messages[0:]
    dialogue = messages[0]["content"] + '\n'
    messages = messages[0:]
    dialogue = get_dialogue(dialogue, messages)

    output = ''
    match = re.search(r'-?\d+(\.\d+)?', output)
    while not match:
        try:
            if type == 1:
                messages = [{"role": "system", "content": prompts.switch},
                            {"role": "user"  , "content": dialogue}]
                output = api.call_api(messages)
            if type == 2:
                instructions = prompts.switch
                messages = [{"role": "user", "content": dialogue}]
                output = api.code_interpreter([file_path], instructions, messages)
            match = re.search(r'-?\d+(\.\d+)?', output)
        except Exception as e:
            log.logger.error(f'Error in call_switch. {{{e}}}')
            return False, None
    
    return True, match.group(0)

def call_case(messages, case, file_path, type):
    match case:
        case 1:  messages[0]["content"] = prompts.case_1
        case 2:  messages[0]["content"] = prompts.case_2
        case 3:  messages[0]["content"] = prompts.case_3
        case 4:  messages[0]["content"] = prompts.case_4
        case 5:  messages[0]["content"] = prompts.case_5
        case 6:  messages[0]["content"] = prompts.case_6
        case 7:  messages[0]["content"] = prompts.case_7
        case 8:  messages[0]["content"] = prompts.case_8
        case 9:  messages[0]["content"] = prompts.case_9
        case 10: messages[0]["content"] = prompts.case_10
        case 11: messages[0]["content"] = prompts.case_11
        # case 12:
        #     dialogue = get_dialogue("", messages[2:])
        #     n_messages = [{"role": "user", "content": messages[1]["content"] + '\n对话记录：\n' + dialogue}]
        #     complete, output = pretreatment.solve_problem(prompts.case_12, n_messages, file_path, type)
        #     if not complete:
        #         return False, None
        #     if output.startswith('【正确】'):
        #         messages[0]["content"] = prompts.case_9
        #     if output.startswith('【错误】'):
        #         complete, output, random = pretreatment.standardize_steps(output)
        #         if not complete:
        #             return False, None
        #         complete = False
        #         start_index = messages[0]["content"].find('#题目：\n') + len('#题目：\n')
        #         end_index = messages[0]["content"].rfind('\n#步骤：\n')
        #         user_input = messages[0]["content"][start_index:end_index].strip() 
        #         n_messages = [{"role": "user"     , "content": prompts.solve_problem + user_input},
        #                       {"role": "assistant", "content": output},
        #                       {"role": "user"     , "content": prompts.check_steps + user_input}]
        #         while not complete:
        #             complete, output = pretreatment.check_steps(n_messages, file_path, type)
        #             if not complete:
        #                 if not output:
        #                     return False, None
        #                 else:
        #                     output = pretreatment.extract_content(output)
        #                     if pretreatment.check_structure(output):
        #                         n_messages.append({"role": "assistant", "content": output})
        #                         n_messages.append({"role": "user"     , "content": '请你结合历史对话，继续对上一轮中的解题步骤进行检查。如果检查无误，请直接通过。'})
        #         messages[1]["content"] += ('\n#修改后的步骤：\n' + output)
        #         messages[0]["content"] = prompts.sub_case_12

    try:
        if type == 1:
            output = api.call_api(messages)
        if type == 2:
            instructions = messages[0]["content"]
            messages = messages[0:]
            messages[0]["content"] += '\n给出的文件中是对于题目的一些补充。'
            output = api.code_interpreter([file_path], instructions, messages)
        messages.append({"role": "assistant", "content": output})
    except Exception as e:
        log.logger.error(f'Error in call_teacher. {{{e}}}')
        return False, None
    
    return True, messages

def call_judge(messages):
    dialogue = get_dialogue("", messages[2:])
    print(dialogue)
    n_messages = [{"role": "system", "content": prompts.judge},
                  {"role": "user"  , "content": dialogue}]
    try:
        output = api.call_api(n_messages)
        while not output.startswith('【通过】'):
            index = output.find('【不通过】：') + len('【不通过】') + 1
            messages[-1]["content"] = output[index:]
            n_messages.append({"role": "assistant", "content": output})
            n_messages.append({"role": "user"     , "content": '请你结合历史对话，继续对上一轮中修改后的内容进行检查。如果检查无误，请直接通过。'})
            output = api.call_api(n_messages)
    except Exception as e:
        log.logger.error(f'Error in call_judge. {{{e}}}')
        return False
    return True

def call_summay(messages):
    return

def init_dialogue(user_input, file_path, type, random):
    complete, messages = call_teacher(user_input, file_path, type, random)
    complete = call_judge(messages)
    return complete, messages

def run_dialogue(user_input, messages, file_path, type):
    messages.append({"role": "user", "content": user_input})
    complete, case = call_switch(messages, file_path, type)
    if complete:
        complete, messages = call_case(messages, case, file_path, type)
        complete = call_judge(messages)
    return complete, messages