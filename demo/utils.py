import gradio as gr

from demo.calls import (
    get_followup_questions,
    get_plotly,
    get_records,
    get_sql,
    get_table,
)


def add_prompt_to_history(history, text):
    history += [(text, None)]
    return history, gr.Textbox(value="", interactive=False)


"""
  chatbot = gr.Chatbot(
        [["Image", gr.Image(value=os.path.join(os.path.abspath(''), "files/avatar.png"), render=False)],
         ["Video", gr.Video(value=os.path.join(os.path.abspath(''), "files/world.mp4"), render=False)],
         ["Audio", gr.Audio(value=os.path.join(os.path.abspath(''), "files/cantina.wav"), render=False)],
         ["Plot", gr.Plot(value=fig, render=False)],
         ["Gallery", gr.Gallery(value=[os.path.join(os.path.abspath(''), "files/lion.jpg"),
                                os.path.join(os.path.abspath(''), "files/cheetah.jpg"),
                                os.path.join(os.path.abspath(''), "files/zebra.jpg")], render=False)]],
        elem_id="chatbot",
        bubble_full_width=False,
        scale=1,
    )
"""

import numpy as np


def event_handler(history):
    prompt = history[-1][0]

    sql = get_sql(prompt)
    records = get_records(sql)
    figure = get_plotly(prompt=prompt, sql=sql, df=records)
    # questions = get_followup_questions(prompt=prompt, sql=sql, records=records)

    print("\nTable:", records, records.shape)

    history.append([None, sql])
    # history.append([None, gr.Dataframe(records)])
    # history.append(["Image", table])
    # history.append([None, figure])
    # df = gr.Dataframe(value=df_orig, interactive=False, row_count=(0, "dynamic"))
    history.append(
        [None, gr.Dataframe(records, interactive=True)]
    )  # , row_count=records.shape[0])])  #row_count=(0, "dynamic"))])
    history.append([None, gr.Plot(figure)])
    # history.append([None, questions])

    return history
