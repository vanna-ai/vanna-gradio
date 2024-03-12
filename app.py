import os
import time

import gradio as gr

# import plotly as pl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import vanna as vn
from dotenv import load_dotenv
from vanna.remote import VannaDefault

pd.options.plotting.backend = "plotly"


# fetch Vanna API key
load_dotenv()

# setup vanna
vn = VannaDefault(model="chinook", api_key=None)  # os.environ.get("VANNA_API_KEY"))
# vn.connect_to_sqlite("https://vanna.ai/Chinook.sqlite")
vn.connect_to_sqlite("Chinook.sqlite")


def add_prompt_to_history(history, text):
    print()
    print("current history:", history)
    history += [(text, None)]
    print("history update:", history)
    return history, gr.Textbox(value="", interactive=False)
    # return history, gr.Code(value="", interactive=True)


def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def prompt2sql(question):
    return vn.generate_sql(question=question)


def sql2records(sql):
    return vn.run_sql(sql=sql)


def records2fig(records):
    placeholder_dataframe = pd.DataFrame(
        {
            "col1": np.random.randint(low=0, high=4, size=300),
            "col2": np.random.randint(low=8, high=15, size=300),
        }
    )

    # placeholder_figure = pl.plot(placeholder_dataframe, kind="hist")

    # placeholder_figure = pd.plotting.hist_frame(placeholder_dataframe)
    # placeholder_figure = pl.histogram(placeholder_dataframe)

    placeholder_figure, ax = plt.subplots()
    ax.hist(placeholder_dataframe)

    plt.show()

    print(placeholder_figure)
    placeholder_figure.savefig("test.jpg")

    # print(placeholder_figure)

    # placeholder_figure.save("test.png")

    return ("test.jpg",)


def fig_bot(history):
    prompt = history[-1][0]

    sql = "Select * FROM Genre"

    records = sql2records(sql)

    print(records)

    history.append([None, sql])

    figure = records2fig(None)

    # history[-1][1] = figure
    history.append([None, figure])

    # history.append([None, ])

    # gr.Plot(value=figure)

    return history


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

    # history[-1][1] = ""
    # for character in sql:
    #    history[-1][1] += character
    #    time.sleep(0.01)
    #    yield history


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
            avatar_images=(None, (os.path.join(os.path.abspath(""), "avatar.png"))),
            rtl=False,
            label=True,
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

        self.plot = gr.Plot()

    def run(self):
        with gr.Blocks() as demo:
            self.chatbot.render()
            # with gr.Row():
            self.question.render()
            # self.code.render()

            txt_msg = self.question.submit(
                add_prompt_to_history,
                [self.chatbot, self.question],
                [self.chatbot, self.question],
                queue=False,
            ).then(
                fig_bot,
                self.chatbot,
                self.chatbot,
                api_name="bot_response",
            )
            # txt_msg.then(lambda: gr.Textbox(interactive=True), None, [user_prompt], queue=False)
            txt_msg.then(
                lambda: gr.Code(interactive=True), None, [self.question], queue=False
            )

            # chatbot.like(print_like_dislike, None, None)

        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
        )


if __name__ == "__main__":
    app = webUI()
    app.run()
