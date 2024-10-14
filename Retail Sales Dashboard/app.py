
from flask import Flask, render_template
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Create Flask app
server = Flask(__name__)

# Create Dash app
app = dash.Dash(__name__, server=server, url_base_pathname='/dashboard/')

# Load your data (you'll need to adjust this path)
sales_df_clean = pd.read_csv('sales 111.csv', 
                             low_memory=False, 
                             parse_dates=['date'])

# Define the Dash layout
app.layout = html.Div([
    html.H1("Retail Sales Dashboard"),
    
    dcc.DatePickerRange(
        id='date-range-picker',
        start_date=sales_df_clean['date'].min(),
        end_date=sales_df_clean['date'].max(),
        max_date_allowed=sales_df_clean['date'].max(),
        min_date_allowed=sales_df_clean['date'].min(),
    ),
    
    dcc.Dropdown(
        id='store-dropdown',
        options=[{'label': store, 'value': store} for store in sales_df_clean['store_id'].unique()],
        value=[sales_df_clean['store_id'].unique()[0]],
        multi=True
    ),
    
    dcc.Graph(id='sales-over-time-graph'),
    dcc.Graph(id='top-products-graph'),
    dcc.Graph(id='store-performance-graph')
])

@app.callback(
    [Output('sales-over-time-graph', 'figure'),
     Output('top-products-graph', 'figure'),
     Output('store-performance-graph', 'figure')],
    [Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date'),
     Input('store-dropdown', 'value')]
)
def update_graphs(start_date, end_date, selected_stores):
    if not isinstance(selected_stores, list):
        selected_stores = [selected_stores]
    
    filtered_df = sales_df_clean[
        (sales_df_clean['date'] >= start_date) & 
        (sales_df_clean['date'] <= end_date) &
        (sales_df_clean['store_id'].isin(selected_stores))
    ]
    
    sales_over_time = filtered_df.groupby('date')['revenue'].sum().reset_index()
    fig1 = px.line(sales_over_time, x='date', y='revenue', title='Sales Over Time')
    
    top_products = filtered_df.groupby('product_id')['revenue'].sum().nlargest(10).reset_index()
    fig2 = px.bar(top_products, x='product_id', y='revenue', title='Top 10 Products by Revenue')
    
    store_performance = filtered_df.groupby('store_id')['revenue'].sum().reset_index()
    fig3 = px.bar(store_performance, x='store_id', y='revenue', title='Store Performance')

    return fig1, fig2, fig3

# Flask routes
@server.route('/')
def index():
    return render_template('index.html')

@server.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    server.run(debug=True)
