from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

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

# Years by Month Line Chart
dm1 = df[['Title', 'monthRead', 'yearRead']]
dm1['bookCount'] = dm1.groupby(['monthRead', 'yearRead']).transform('count')
dm1[['monthRead']] = dm1[['monthRead']].astype(int)
dm1 = dm1[['bookCount', 'monthRead', 'yearRead']]
dm1 = dm1.drop_duplicates()
dm1 = dm1.sort_values(by=['monthRead'], ascending=True)
print(dm1)

# Initialize the app - incorporate css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Books & Pages Line Chart

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=year, y=books, name="Books"),
    secondary_y=False,
)
fig.add_trace(
    go.Scatter(x=year, y=pages, name="Pages"),
    secondary_y=True,
)
fig.update_layout(title_text="Number of Books & Pages by Year",)
fig.update_xaxes(title_text="Year")
fig.update_yaxes(
    title_text="Books",
    secondary_y=False)
fig.update_yaxes(
    title_text="Pages",
    secondary_y=True)

month = px.line(dm1, x="monthRead", y="bookCount", color='yearRead')
month.update_layout(title_text="Number of Books Read by Year and Month")
month.update_xaxes(title_text="Month")
month.update_yaxes(title_text="Number of Books")

# Page Range Pie Chart
dp1 = df[['Number of Pages']]
dp1 = dp1[~dp1['Number of Pages'].isnull()]
dp1[['Number of Pages']] = dp1[['Number of Pages']].astype(int)
dp1 = dp1.rename(columns={'Number of Pages': 'numPages'})

page_groups = [0, 150, 300, 500, 800, 1000]

for i in range(len(page_groups) - 1):
    subset = dp1.query(
        f'numPages >= {page_groups[i]} & numPages < {page_groups[i+1]}')
    dp1.loc[subset.index, 'page_bin'] = i

dp2 = pd.DataFrame(dp1.page_bin.value_counts(
).reset_index().values, columns=["Range", "Number"])
dp2 = dp2.sort_values(by='Number', ascending=False)
dp2['Range'] = dp2['Range'].map({0.0: 'Under 150', 1.0: 'Between 150 & 300',
                                 2.0: 'Between 300 & 500', 3.0: 'Between 500 & 800',
                                 4.0: 'Between 800 & 1000'})

# Publication Range Pie Chart
dpb1 = df[['Original Publication Year']]
dpb1 = dpb1[~dpb1['Original Publication Year'].isnull()]
dpb1[['Original Publication Year']] = dpb1[['Original Publication Year']].astype(int)
dpb1 = dpb1.rename(columns={'Original Publication Year': 'yearPub'})

pub_groups = [0,1900,1950,2000,2010,2015,2023]
for i in range(len(pub_groups) - 1):
    subset = dpb1.query(f'yearPub >= {pub_groups[i]} & yearPub < {pub_groups[i+1]}')
    dpb1.loc[subset.index, 'pub_bin'] = i

dpb2 = pd.DataFrame(dpb1.pub_bin.value_counts().reset_index().values, columns=["Range", "Number"])
dpb2 = dpb2.sort_values(by='Number',ascending=False)
dpb2['Range'] = dpb2['Range'].map({0.0: 'Before 1900', 1.0: 'Between 1900 & 1950',
                                 2.0: 'Between 1950 & 2000', 3.0: 'Between 2000 & 2010',
                                 4.0: 'Between 2010 & 2015', 5.0: 'Between 2015 & 2023'})

# App layout
app.layout = html.Div([
    html.Div(className='row', children=[
        html.Div(className='five columns', children=[
            dcc.Graph(figure=px.box(db3, x="Type of Rating", y='Rating',
                                    title="Distribution of My Reviews vs the Goodreads Average"))
        ]),

        html.Div(className='seven columns', children=[
            dcc.Graph(figure=fig),
        ]),
    ]),

    html.Div(className='row', children=[
        html.Div(className='five columns', children=[
            html.H1("Most Read Authors & Their Average Ratings",
                    style={'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '40px', 'margin-top': '40px',
                           'letter-spacing': '1px'}),
            dash_table.DataTable(data=da2.to_dict('records'),
                                 style_cell={'padding-top': '30px',
                                             'textAlign': 'left'},
                                 style_table={
                                     'margin-left': '40px'}
                                 ),
        ]),
        html.Div(className='seven columns', children=[
            dcc.Graph(figure=month),
        ]),
    ]),

    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            dcc.Graph(figure=px.pie(dp2, values='Number', names='Range',title="Books Read by Page Range")),
        ]),
        html.Div(className='six columns', children=[
            dcc.Graph(figure=px.pie(dpb2, values='Number', names='Range',title="Books Read by Publication Range"))
        ]),
    ])
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
