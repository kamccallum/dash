from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import base64

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
fig.update_xaxes(title_text="Year")
fig.update_yaxes(
    title_text="Books",
    secondary_y=False)
fig.update_yaxes(
    title_text="Pages",
    secondary_y=True)

month = px.line(dm1, x="monthRead", y="bookCount", color='yearRead')
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
dpb1[['Original Publication Year']] = dpb1[[
    'Original Publication Year']].astype(int)
dpb1 = dpb1.rename(columns={'Original Publication Year': 'yearPub'})

pub_groups = [0, 1900, 1950, 2000, 2010, 2015, 2023]
for i in range(len(pub_groups) - 1):
    subset = dpb1.query(
        f'yearPub >= {pub_groups[i]} & yearPub < {pub_groups[i+1]}')
    dpb1.loc[subset.index, 'pub_bin'] = i

dpb2 = pd.DataFrame(dpb1.pub_bin.value_counts(
).reset_index().values, columns=["Range", "Number"])
dpb2 = dpb2.sort_values(by='Number', ascending=False)
dpb2['Range'] = dpb2['Range'].map({0.0: 'Before 1900', 1.0: 'Between 1900 & 1950',
                                   2.0: 'Between 1950 & 2000', 3.0: 'Between 2000 & 2010',
                                   4.0: 'Between 2010 & 2015', 5.0: 'Between 2015 & 2023'})
# App layout
app.layout = html.Div([
    html.Img(src='assets/mdtFull.png', className='logo', id='logo'),
    html.Img(src='assets/arrow.png', className='arrow'),
    html.H2('Frustrated with Goodreads, a lone student decided to strike out on her own…',
            className='animation'),
    html.Img(src='assets/frame1.png', style={'width': '300px',
             'margin-bottom': '300px', 'margin-left': '200px'}, className='animation'),
    html.H2('She traversed the wild web, tripping over a number of curiosities (React, Django, Matplotlib),',
            style={'textAlign': 'right'}, className='animation'),
    html.Img(src='assets/frame2.png', className='animation', id='frame2'),
    html.H2('until finally stumbling upon a humble, yet welcome, abode: Dash...',
            className='animation'),
    html.Img(src='assets/frame3.png', style={'width': '300px',
             'margin-bottom': '100px', 'margin-left': '200px'}, className='animation'),

    html.Div(className='row', children=[
        html.H1('Goodreads Data Visualizations', className='title'),
        html.A('(or jump to description)', className='jump', href='#about'),
        html.Div(className='five columns', children=[
            html.H1("Distribution of Reviews",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '70px', 'margin-top': '40px',
                    }),
            dcc.Graph(figure=px.box(db3, x="Type of Rating",
                      y='Rating'), style={'margin-top': '-10px'}),
        ]),

        html.Div(className='six columns', children=[
            html.H1("Number of Books & Pages by Year",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '80px', 'margin-top': '40px',
                    }),
            dcc.Graph(figure=fig, style={'margin-top': '-20px'}),
        ]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.P('Description: displays the distribution of my reviews alongside the distribution of the average Goodreads reviews for the same \
                books.', style={
                'margin-left': '80px'}),
            html.P('Takeaway: my outliers are substantially lower than the average review distribution. So, although the median is fairly similar,\
                I give out more high and low ratings than the average user. This makes sense, considering that one is a distribution of averages, which is expected to have a smaller spread.', style={'margin-left': '80px'}),
        ]),
        html.Div(className='six columns', children=[
            html.P('Description: the number of books and pages that I read every year, from the end of 2013 to the beginning of 2023. The books read in 2013 and 2023 were not recorded in full.', style={
                'margin-right': '80px', 'margin-left': '0px'}),
            html.P('Takeaway: I read the most books and pages in 2015, closely followed by 2022. As expected, books and pages are closely correlated to one another.', style={
                'margin-right': '80px', 'margin-left': '0px'}),
        ]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='five columns', children=[
            html.H1("Most Read Authors",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '80px', 'margin-top': '120px',
                    }),
            dash_table.DataTable(data=da2.to_dict('records'),
                                 style_cell={'padding-top': '30px',
                                             'textAlign': 'left'},
                                 style_table={
                                     'margin-left': '80px', 'width': '80%', 'margin-top': '20px'}
                                 ),
        ]),
        html.Div(className='seven columns', children=[
            html.H1("Number of Books by Year and Month",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '130px', 'margin-top': '40px',
                    }),
            dcc.Graph(figure=month, style={
                      'width': '87%', 'margin-left': '60px'}),
        ]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.P('Description: the five authors whom I have read the most, alongside the number of books I have read by them and the average rating that I gave them across all of these books.', style={
                'margin-left': '80px'}),
            html.P('Takeaway: despite Jennifer L. Armentrout being in the top 5, she has a relatively low average rating. I should perhaps stop reading books by her.', style={
                   'margin-left': '80px'}),
        ]),
        html.Div(className='six columns', children=[
            html.P('Description: the number of books that I read throughout the year, with different colored lines displaying each year.', style={
                   'margin-left': '0px'}),
            html.P('Takeaway: 2016 and 2015 peak in July, during summer break. There is also a peak in December of 2015, which would have been winter break. Unsurprisingly, \
                I read more when out of school.', style={'margin-left': '0px'}),
        ]),
    ]),

    html.Div(className='row', style={'display': 'block'}, children=[
        html.Div(className='six columns', children=[
            html.H1("Books Read by Page Range",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '80px', 'margin-top': '40px',
                    }),
            dcc.Graph(figure=px.pie(dp2, values='Number',
                      names='Range'), style={'margin-left': '40px'}),
        ]),
        html.Div(className='five columns', children=[
            html.H1("Books Read by Publication Range",
                    style={  # 'color': 'grey', 'fontSize': 18, 'font-family': 'Verdana',
                           'margin-left': '80px', 'margin-top': '40px',
                    }),
            dcc.Graph(figure=px.pie(dpb2, values='Number',
                      names='Range'), style={'margin-left': '0px'})
        ]),
    ]),
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            html.P('Description: percentage of books read by page range.', style={
                'margin-left': '80px'}),
            html.P('Takeaway: the majority of books I read are between 300 and 500 pages long. I rarely read books that are under 150 pages and books that are between 800 and 1000 pages.', style={
                   'margin-left': '80px', 'margin-bottom': '60px'}),
        ]),
        html.Div(className='six columns', children=[
            html.P('Description: percentage of books read by original publication year as a range.', style={
                   'margin-left': '0px'}),
            html.P('Takeaway: the majority of books I read were published between 2015 and 2023. I rarely read books published prior to 1900 and books published between 1900 and 1950.', style={
                   'margin-left': '0px', 'margin-bottom': '60px'}),
        ]),
    ]),
    html.Div(className='row', style={'margin-top': '60px'}, children=[
        html.H1('About', id='about'),
        html.H3('Summary'),
        html.P("My Data Tales was created for Fordham University's New Media and Digital Design capstone course. As an avid reader, Kyla \
                likes to track her books via a popular tool called Goodreads. At the end of the year, Goodreads presents user-centered \
                data visualizations on the 'Year in Books' page, similar to Spotify's Wrapped feature. However, Kyla took a course on data \
                visualization in Spring of 2022, and she saw many opportunities to expand upon Goodreads's annual 'Year in Books.' Rather \
                than using Figma to prototype improvements in Goodreads, she decided to implement these changes herself. This website is \
                the culmination of a semester's worth of research on programming. Kyla had minimal experience prior to undertaking this \
                project, with only an 'Introduction to Computer Programming' class under her belt. She substantially built upon her familiarity \
                with pandas, a python data analysis tool, and started from scratch with plotly/dash. If it had been clear from the get-go \
                that these two tools, pandas and plotly, were the best for her project, a lot of time would have been saved; \
                many avenues were explored that did not pan out. Fortunately, Kyla learned a lot, even if this website doesn't demonstrate \
                all of her efforts. To display the complexity of her work with data, please see screenshots below:"),
        html.Div(className='row covers', style={'margin-top': "40px", 'padding-left': '70px'}, children=[
            html.Div(className='six columns', children=[
                html.Img(src='assets/csvFile.png', style={'width': '100%'}),
                html.P('The Goodreads CSV file, which has 857 rows'),
            ]),
            html.Div(className='five columns', children=[
                html.Img(src='assets/pandasCSV.png', style={'width': '90%'}),
                html.P('Preparing data in pandas'),
            ]),
        ]),
        html.Div(className='row covers', style={'margin-top': '30px', 'padding-left': '70px'}, children=[
            html.Div(className='five columns', style={'height': '550px'}, children=[
                html.Img(src='assets/pandasLine.png', style={'width': '100%'}),
                html.P('Data manipulation for a line chart'),
            ]),
            html.Div(className='six columns', children=[
                html.Img(src='assets/pandasPie.png', style={'width': '90%'}),
                html.P('Data manipulation for a pie chart'),
            ]),
        ]),
    ]),
    html.Img(src='assets/mdt_init.png', className='Footer'),
    html.Div(id='footer', className='row', children=[
        html.A('Back to Top', href='#logo'),
        html.A('Built by Kyla McCallum', href='https://kamccallum.github.io/', target='_blank', style={
            'padding-top': '30px', 'padding-bottom': '30px', 'text-align': 'center', 'width': '100%'}),
    ]),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
