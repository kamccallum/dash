from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Incorporate data
df = pd.read_csv('goodreads_library.csv')
df = df.loc[df['Exclusive Shelf'] == 'read']
df[['monthRead', 'dayRead', 'yearRead']
   ] = df['Date Read'].str.split('/', expand=True)
df = df[~df['yearRead'].isnull()]
df = df[~df['monthRead'].isnull()]
df[['yearRead']] = df[['yearRead']].astype(int)
df[['My Rating']] = df[['My Rating']].astype(float)
df[['Average Rating']] = df[['Average Rating']].astype(float)

# Boxplot of my ratings versus average ratings
myRating = list(df['My Rating'])
myRating = [i for i in myRating if i != 0]

aveRating = list(df['Average Rating'])
aveRating = [i for i in aveRating if i != 0]

db1 = pd.DataFrame(myRating)
db1 = db1.assign(type="My Rating")

db2 = pd.DataFrame(aveRating)
db2 = db2.assign(type="Average Rating")

db3 = pd.merge(db1, db2, how='outer')
db3 = db3.rename(columns={0: 'Rating', 'type': 'Type of Rating'})

# Line chart of books read and pages read
df1 = df.copy(deep=True)
df1['book_count'] = df1.groupby('yearRead')['yearRead'].transform('count')
df1 = df1[['book_count', 'yearRead']]
df1 = df1.drop_duplicates()
df1 = df1.sort_values(by='yearRead', ascending=True)
df1 = df1.rename(columns={'book_count': 'Books', 'yearRead': 'Year'})
books = list(df1["Books"])

df2 = df.copy(deep=True)
df2 = df2.groupby(['yearRead'])
df2 = df[['Number of Pages', 'yearRead']]
df2 = df2.rename(columns={'Number of Pages': 'Pages', 'yearRead': 'Year'})
df2 = df2.groupby(pd.Grouper(key="Year")).sum()
df2 = df2.sort_values(by='Year', ascending=True)
pages = list(df2["Pages"])

year = ['2013', '2014', '2015', '2016', '2017',
        '2018', '2019', '2020', '2021', '2022', '2023']

# Top 5 authors and their ratings
da1 = df[df['My Rating'] != 0]
da2 = da1[['Author', 'My Rating']]
da2 = da2['Author'].value_counts().to_frame('Number of Books')
da2 = da2.sort_values(by='Number of Books', ascending=False)
da2 = da2.head()

da3cc = da1[da1['Author'] == 'Cassandra Clare']

da3rr = da1[da1['Author'] == 'Rick Riordan']

da3sm = da1[da1['Author'] == 'Sarah J. Maas']

da3mm = da1[da1['Author'] == 'Marissa Meyer']

da3ja = da1[da1['Author'] == 'Jennifer L. Armentrout']

author = ['Cassandra Clare', 'Rick Riordan', 'Sarah J. Maas',
          'Marissa Meyer', 'Jennifer L. Armentrout']
ratings = [4.928571428571429, 4.384615384615385,
           4.6, 4.428571428571429, 3.142857142857143]

da2['Authors'] = author
da2['Ave Rating'] = ratings
da2 = da2.iloc[:, [1, 0, 2]]
print(da2)

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = html.Div([
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.Div('Distribution of Ratings',
                 style={'color': 'white', 'fontSize': 20, "margin-top": "15px", 'font-family': "Helvetica"}),
            dcc.Graph(figure=px.box(db3, x="Type of Rating",
                      y='Rating'))
        ]),

        html.Div(className='six columns', children=[
            dcc.RadioItems(
                id='radio',),
            html.Div('Number of Books and Pages by Year',
                     style={'color': 'white', 'fontSize': 20, "margin-top": "15px", 'font-family': "Helvetica"}),
            dcc.Graph(id="graph"),
        ]),
    ]),

    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.Div('Most Read Authors & Their Average Ratings',
                 style={'color': 'white', 'fontSize': 20, "margin-top": "15px", 'font-family': "Helvetica"}),
            dash_table.DataTable(data=da2.to_dict('records')),
        ]),
        html.Div(className='six columns', children=[
            html.Div('Distribution of Ratings',
                 style={'color': 'white', 'fontSize': 20, "margin-top": "15px", 'font-family': "Helvetica", 'font-weight': 'normal'}),
        ]),
    ]),
])


@ app.callback(
    Output('graph', 'figure'),
    Input('radio', 'value')
)
def display_(radio_value):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(x=year, y=books, name="Books"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=year, y=pages, name="Pages"),
        secondary_y=True,
    )

    fig.update_xaxes(title_text="Year")

    fig.update_yaxes(
        title_text="Books",
        secondary_y=False)
    fig.update_yaxes(
        title_text="Pages",
        secondary_y=True)
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
