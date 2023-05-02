from dash import Dash, html, dash_table, dcc
import pandas as pd
import plotly.express as px

# Incorporate data
df = pd.read_csv('goodreads_library.csv')
df[['monthRead', 'dayRead', 'yearRead']] = df['Date Read'].str.split('/', expand=True)
df = df[~df['yearRead'].isnull()]
df = df[~df['monthRead'].isnull()]
df[['yearRead']] = df[['yearRead']].astype(int)
df[['myRating']] = df[['My Rating']].astype(int)

data = df['myRating']

df['freq_count'] = df.groupby('yearRead')['yearRead'].transform('count')
df1 = df[['freq_count','yearRead']]
df1 = df1.drop_duplicates()
df1 = df1.sort_values(by='yearRead',ascending=True)
df1 = df1.rename(columns={'freq_count': 'Total', 'yearRead': 'Year'})
df1 = df1.iloc[:,[1,0]]
df1 = df1.reset_index(drop=True)

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = html.Div([
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            dcc.Graph(figure=px.line(df1, x='Year', y='Total', title='Books Read by Year')),
        ]),
        html.Div(className='six columns', children=[
            dcc.Graph(figure= px.box(data, y='myRating', title='Distribution of Book Ratings')),
        ]),
    ])
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)