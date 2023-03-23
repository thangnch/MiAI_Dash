from dash import Dash, html, dcc
from dash.dependencies import Input,Output
import plotly.express as px
import pandas as pd

app = Dash()
server = app.server

def fix_km(x):
    return x.replace(" Km","").replace(",","")

# Đọc dữ liệu từ file car.csv
car_df = pd.read_csv("data/car.csv", delimiter="|", on_bad_lines="skip")
car_df["km"] = car_df["km"].apply(fix_km)
print(car_df.head())

# Tạo ra 1 list hãng xe để đưa vào combo
car_brand_list = []
for brand in sorted(set(car_df["car_model"].values)):
    car_brand_list.append({
        "label": brand,
        "value": brand
    })

# Tạo ra 1 list gồm All, Nhập khẩu, trong nươc
imp_exp_list = []

imp_exp_list.append({
        "label": "All",
        "value": "All"
    })

for imp_exp in sorted(set(car_df["imp_exp"].values)):
    imp_exp_list.append({
        "label": imp_exp,
        "value": imp_exp
    })

# Dựng layout
app.layout = html.Div(
    [
        html.H1("Car Price Data App by Miai.vn", style={"textAlign":"center"}),
        html.Div(
            [
                html.Div("Nhãn hiệu xe: ", style={"textAlign":"center"}),
                dcc.Dropdown(
                    id="car_brand_dropdown",
                    multi=True,
                    style={"display": "block", "margin-left": "auto",
                            "margin-right": "auto", "width": "60%"},
                    options= car_brand_list,
                    value= [car_brand_list[0]['value']]# Gia tri chon mac dinh luc dau
                ),
                html.Div("Loại xe: ", style={"textAlign":"center"}),
                dcc.Dropdown(
                    id="car_type_dropdown",
                    style={"display": "block", "margin-left": "auto",
                            "margin-right": "auto", "width": "60%"},
                    options= imp_exp_list,
                    value= imp_exp_list[0]['value']# Gia tri chon mac dinh luc dau
                ),
                html.Br(),
                html.Div(
                    [
                        html.Span(
                            [
                                html.Span('Từ năm:', style={"textAlign": "center"}),
                                dcc.Input(id='from_year', value='1900', type='number',debounce = True)
                            ]
                        ),
                        html.Span(' '),
                        html.Span(
                            [
                                html.Span('Đến năm:', style={"textAlign": "center"}),
                                dcc.Input(id='to_year', value='2023', type='number',debounce = True)
                            ]
                        )
                    ], style={"textAlign": "center"}
                ),
                dcc.Graph(id="histogram_chart"),
                dcc.Graph(id="pie_chart")
            ]
        )
    ]
)

# Phần Callback
@app.callback(
    Output('histogram_chart', 'figure'), Output('pie_chart', 'figure'),
    Input('car_brand_dropdown','value'),Input('car_type_dropdown','value'),Input('from_year','value'),Input('to_year','value')
)
def update_charts(car_brand_dropdown,car_type_dropdown,from_year,to_year):
    f_df = car_df[car_df.car_year != "< 1990"]
    if len(car_brand_dropdown) > 0:
        f_df = f_df[f_df.car_model.isin(car_brand_dropdown)]

    if car_type_dropdown!="All":
        f_df = f_df[f_df.imp_exp ==car_type_dropdown]

    if from_year!="":
        f_df = f_df[f_df.car_year.astype(int) >= int(from_year)]

    if to_year!="":
        f_df = f_df[f_df.car_year.astype(int) <= int(to_year)]

    fig_histogram = px.histogram(f_df, x = "km")

    g_df = f_df.groupby(["out_color"]).size().reset_index(name='count')
    fig_pie = px.pie(g_df, values="count", names="out_color")

    return fig_histogram, fig_pie

app.run_server(debug=True, host='0.0.0.0', port='8888')

#ipconfig in Commandline
#ngrok