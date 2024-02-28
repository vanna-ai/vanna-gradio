import os
import time

from dotenv import load_dotenv
import gradio as gr
import vanna as vn
from vanna.remote import VannaDefault
import pandas as pd


# fetch Vanna API key
load_dotenv()

# setup vanna
vn = VannaDefault(model="chinook", api_key=os.environ.get("VANNA_API_KEY"))
vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")


def add_prompt_to_history(history, text):
    print()
    print("current history:", history)
    history += [(text, None)]
    print("history update:", history)
    return history, gr.Textbox(value="", interactive=False)
    #return history, gr.Code(value="", interactive=True)


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def prompt2sql(question):
    return vn.generate_sql(question=question)


def sql2records(sql):
    return vn.run_sql(sql=sql)


def bot(history):
    print("history:", history)
    prompt = history[-1][0]
    sql = prompt2sql(prompt)
    print("sql:", sql)

    try:
        records = sql2records(sql)
        records.to_csv("tmp.csv")
        print(records)
    except Exception as e:
        print(e)
        # records = pd.DataFrame()
    
    history[-1][1] = "tmp.csv"

    return history
    
    #history[-1][1] = ""
    #for character in sql:
    #    history[-1][1] += character
    #    time.sleep(0.01)
    #    yield history


"""
    gr.Chatbot([
        ("Show me an image and an audio file", "Here is an image"), 
        (None, ("avatar.png",)), 
    ])
"""


class webUI:
    def __init__(self):
        self.history = []
        self.events = []

        self.create_components()
    
    def create_components(self):
        self.chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=False,
            avatar_images=(None, (os.path.join(os.path.abspath(''), "avatar.png"))),
        )

        self.question = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="Which artists are in the database?",
            container=False,
        )

        self.code = gr.Code(
            interactive=True,
        )
    
    def run(self):
        with gr.Blocks() as demo:
            self.chatbot.render()
            #with gr.Row():
            self.question.render()
            # self.code.render()
            
            txt_msg = self.question.submit(add_prompt_to_history, [self.chatbot, self.question], [self.chatbot, self.question], queue=False).then(
                bot, self.chatbot, self.chatbot, api_name="bot_response",
            )
            #txt_msg.then(lambda: gr.Textbox(interactive=True), None, [user_prompt], queue=False)
            txt_msg.then(lambda: gr.Code(interactive=True), None, [self.question], queue=False)

            # chatbot.like(print_like_dislike, None, None)

        demo.queue().launch(
            server_name="0.0.0.0", server_port=7860, share=False,
        )


if __name__ == "__main__":
    app = webUI()
    app.run()
