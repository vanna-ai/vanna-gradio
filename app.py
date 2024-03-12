import os

import gradio as gr
import plotly.graph_objects as go
import vanna as vn

from src.setup import setup_vanna

vn = setup_vanna(vn=vn)


# vn.ask("What are the top 10 albums by sales?")


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


def get_followup_questions(prompt, records):
    top3 = vn.generate_followup_questions(question=prompt, df=records)[:3]
    top3 = "\n".join(top3)
    top3 = "Candidate follow up questions:\n" + top3

    return top3


def records2fig(prompt, sql, df):
    code = vn.generate_plotly_code(question=prompt, sql=sql, df=df)
    fig = vn.get_plotly_figure(plotly_code=code, df=df)
    fig.write_image("plotly.jpg")

    return ("plotly.jpg",)


def records2table(records):
    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=list(records.columns),
                    fill_color="paleturquoise",
                    align="left",
                ),
                cells=dict(
                    values=records.transpose().values.tolist(),
                    fill_color="lavender",
                    align="left",
                ),
            )
        ]
    )
    fig.write_image("table.jpg")

    return ("table.jpg",)


def bot(history):
    prompt = history[-1][0]
    # sql = "Select * FROM Genre"
    sql = prompt2sql(prompt)
    records = sql2records(sql)
    table_figure = records2table(records)
    figure = records2fig(prompt=prompt, sql=sql, df=records)
    follow_up_questions = get_followup_questions(prompt=prompt, records=records)

    history.append([None, sql])
    history.append([None, table_figure])
    history.append([None, figure])
    history.append([None, follow_up_questions])

    return history


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
            height=800,
        )

        self.question = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="What are the top 10 albums by sales?",
            container=False,
        )

        self.code_editor = gr.Code(
            interactive=True,
            lines=51,
        )

        self.plot = gr.Plot()

    def like_dislike_event(self):
        pass

    def run(self):
        with gr.Blocks() as demo:
            with gr.Row():
                # chatbot column
                with gr.Column():
                    self.chatbot.render()
                    self.question.render()

                    txt_msg = self.question.submit(
                        add_prompt_to_history,
                        [self.chatbot, self.question],
                        [self.chatbot, self.question],
                        queue=False,
                    ).then(
                        bot,
                        self.chatbot,
                        self.chatbot,
                        api_name="bot_response",
                    )
                    # txt_msg.then(lambda: gr.Textbox(interactive=True), None, [user_prompt], queue=False)
                    txt_msg.then(
                        lambda: gr.Code(interactive=True),
                        None,
                        [self.question],
                        queue=False,
                    )

                    self.chatbot.like(self.like_dislike_event, None, None)

                # code correction column
                with gr.Column():
                    self.code_editor.render()

        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
        )


if __name__ == "__main__":
    app = webUI()
    app.run()
