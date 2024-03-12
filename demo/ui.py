import os

import gradio as gr

from .utils import add_prompt_to_history, event_handler


class WebUI:
    def __init__(self):
        self.history = []
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

                    self.chatbot.like(self.like_dislike_event, None, None)

                # code correction column
                with gr.Column():
                    self.code_editor.render()

        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
        )
