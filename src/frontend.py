import dialogue
import pretreatment
import css
import gradio as gr
import json

def user(history, input):
    return history + [[input, None]], ""

def bot(history, messages, file_path, type):
    complete, n_messages = dialogue.run_dialogue(history[-1][0], messages, file_path, type)
    if complete:
        return history + [[None, n_messages[-1]["content"]]], n_messages
    else:
        return [["ERROR", None]], []

def reset(problem, radio, file_path):
    type = 0
    if radio == "否" or radio == None:
        type = 1
        file_path = ""
    else:
        type = 2
    complete, random = pretreatment.get_steps(problem, file_path, type)
    if complete:
        complete, messages = dialogue.init_dialogue(problem, file_path, type, random)
        if complete:
            chatbot = [[None, "## ————————————————苏格拉底式教学助手———————————————— ##"], [None, messages[-1]["content"]]]
            return chatbot, messages, file_path, type, random
    else:
        return [['ERROR', None]], [], '', 0, '' 

def files(messages, random):
    file_name = 'history/history-' + random + '.json'
    dialogue = [messages[1]["content"]]
    for message in messages[2:]:
        if message["role"] == "user":
            dialogue.append('#学生：' + message["content"] + '\n')
        if message["role"] == "assistant":
            dialogue.append('#老师：' + message["content"] + '\n')
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(dialogue, file, ensure_ascii=False, indent=4)
    return file_name

with gr.Blocks(css=css.css) as iface:
    messages = gr.State(value=[])
    path     = gr.State(value="")
    type     = gr.State(value=0)
    random   = gr.State(value="")
    with gr.Column(variant="default", elem_classes="outer"):
        chatbot = gr.Chatbot(label="对话", value=[[None, "## ————————————————苏格拉底式教学助手———————————————— ##"]], elem_classes="dialogue_box")
        input   = gr.Textbox(label="输入", elem_classes="input_box", placeholder="在此输入以进行对话...")
        with gr.Row():
            with gr.Column(variant="default", elem_classes="column_box"):
                problem = gr.TextArea(label="题目", placeholder="在此输入题目...", elem_classes="problem_box", max_lines=1)
                with gr.Row():
                    radio     = gr.Radio(["是", "否"], label="是否需要添加附件", elem_classes="addon_box")
                    file_path = gr.Textbox(label="附件路径（如果需要）", elem_classes="addon_box", placeholder="在此输入文件路径...", max_lines=1)
            with gr.Column(variant="default", elem_classes="column_box"):
                restart  = gr.Button("开始/重新开始", elem_classes="restart_button")
                download = gr.Button("下载对话记录", elem_classes="download_button")
                file     = gr.File(label="下载", interactive=False, elem_classes="download_box")

    input.submit(user, [chatbot, input], [chatbot, input]).then(bot, [chatbot, messages, file_path, type], [chatbot, messages])
    restart.click(reset, [problem, radio, file_path], [chatbot, messages, path, type, random])
    download.click(files, [messages, random], file)