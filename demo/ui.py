import os

import gradio as gr
import vanna as vn

from .utils import add_prompt_to_history, event_handler


class WebUI:
    def __init__(self):
        self.history = []
        self.current_question = None
        self.current_code = ""
        self.indices = []
        self.create_components()

    def create_components(self):
        self.chatbot = gr.Chatbot(
            [],
            elem_id="chatbot",
            bubble_full_width=False,
            avatar_images=(None, (os.path.join(os.path.abspath(""), "avatar.png"))),
            rtl=False,
            label="Chatbot",
            height=800,
        )

        self.question = gr.Textbox(
            scale=4,
            show_label=False,
            placeholder="What are the top 10 albums by sales?",
            container=False,
            elem_id="textbox",
        )

        self.code_editor = gr.Code(
            interactive=True,
            lines=51,
            # every=1,
            value=self.update_code,
            language="sql",
            elem_id="code_editor",
        )

        self.clear_chat_button = gr.Button(
            value="Clear chat",
            variant="secondary",
            elem_id="clear_chat",
        )

        self.clear_code_button = gr.Button(
            value="Clear code",
            variant="secondary",  # "stop"
            elem_id="clear_code",
        )

        self.save_button = gr.Button(
            value="Save question-sql pair",
            variant="primary",
            elem_id="save_pair",
        )

    def update_code(self):
        return self.current_code

    def get_vote(self, data: gr.LikeData, history):
        if data is None:
            return

        # ignore thumbs up events
        if data.liked:
            print("Thumbs up event happened (but did nothing!)")
            return history

        print(data.value)

        # handle if SQL string
        if isinstance(data.value, str) and ("SELECT" in data.value):
            self.current_code = data.value
            return history

        current = data.value["file"]["mime_type"]

        if current == "image/jpeg":
            pass

    def train_on_prompt_sql(self):
        print("training vanna...")
        vn.train(question=self.current_question, sql=self.current_code)
        print("Done!")

    def clear_chat(self, history):
        self.current_question = None
        self.clear_code()  # also clears code
        return []

    def clear_code(self):
        self.current_code = ""

    def run(self):
        with gr.Blocks() as demo:
            with gr.Row():
                # chatbot column
                with gr.Column():
                    self.clear_chat_button.render()
                    self.clear_chat_button.click(
                        self.clear_chat, self.chatbot, self.chatbot
                    )

                    self.chatbot.render()
                    self.question.render()

                    txt_msg = self.question.submit(
                        add_prompt_to_history,
                        [self.chatbot, self.question],
                        [self.chatbot, self.question],
                        queue=False,
                    ).then(
                        event_handler,
                        self.chatbot,
                        self.chatbot,
                        api_name="bot_response",
                    )
                    txt_msg.then(
                        lambda: gr.Code(interactive=True),
                        None,
                        [self.question],
                        queue=False,
                    )

                    self.chatbot.like(
                        self.get_vote, [self.chatbot], [self.chatbot]
                    )  # .then(self.get_vote, None, self.code_editor)

                # code correction column
                with gr.Column():
                    with gr.Row():
                        self.clear_code_button.render()
                        self.clear_code_button.click(self.clear_code)

                        self.save_button.render()
                        self.save_button.click(self.train_on_prompt_sql)

                    self.code_editor.render()
                    self.code_editor.focus(self.update_code, None, self.code_editor)

                    # self.code_editor.input(self.update_code, None, None)

                    # interface = gr.Interface(fn=self.get_vote, inputs=self.chatbot, outputs=self.code_editor)

        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
        )
