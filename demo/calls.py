import plotly.graph_objects as go
import vanna as vn

from .setup import setup_vanna

vn = setup_vanna(vn=vn)


def get_sql(question):
    return vn.generate_sql(question=question)


def get_records(sql):
    return vn.run_sql(sql=sql)


def get_followup_questions(prompt, records):
    top3 = vn.generate_followup_questions(question=prompt, df=records)[:3]
    top3 = "\n".join(top3)
    top3 = "Candidate follow up questions:\n" + top3
    return top3


def get_plotly(prompt, sql, df):
    code = vn.generate_plotly_code(question=prompt, sql=sql, df=df)
    fig = vn.get_plotly_figure(plotly_code=code, df=df)
    fig.write_image("plotly.jpg")
    return ("plotly.jpg",)


def get_table(records):
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
