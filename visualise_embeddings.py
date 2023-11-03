import dash
import numpy as np
import umap
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA

app = dash.Dash(__name__)

# Load your data
embeddings = np.load('vis_data/wandsworth_house_facade_image_embeddings_np.npy')
metadata = pd.read_csv('vis_data/house_facades_metadata.csv')

# Perform PCA on the embeddings to reduce dimensionality
# pca = PCA(n_components=2)  # You can adjust the number of components as needed
# embedding_pca = pca.fit_transform(embeddings)

# Add the PCA components to the metadata
# metadata['PCA1'] = embedding_pca[:, 0]
# metadata['PCA2'] = embedding_pca[:, 1]

# Perform UMAP dimensionality reduction on the embeddings
umap_model = umap.UMAP(n_components=2, random_state=42)
embedding_umap = umap_model.fit_transform(embeddings)

# Add the UMAP components to the metadata
metadata['UMAP1'] = embedding_umap[:, 0]
metadata['UMAP2'] = embedding_umap[:, 1]

# Add image URLs to customdata
metadata['customdata'] = metadata['image_url']

color_scale = px.colors.qualitative.Set1

background_color = 'rgba(215, 66, 90, 0.1)'  # Background color: #D7425A with an alpha of 25%
# background_color = 'rgba(0, 0, 0, 0)'
point_color = '#6C63FF'  # Point color: #6C63FF

app.layout = html.Div([
    dcc.Graph(id='embedding-plot'),
    html.Img(id='image-display', src='', style={'width': '300px', 'height': '200px'}),  # Placeholder for the displayed image
    dcc.Input(id='dummy-input', value=0, type='hidden')
])

@app.callback(
    [Output('embedding-plot', 'figure'), Output('image-display', 'src')],
    [Input('dummy-input', 'value'), Input('embedding-plot', 'clickData')]
)
def update_plot_and_image(value, click_data):
    fig = px.scatter(
        metadata,
        # x='PCA1',
        # y='PCA2',
        x='UMAP1',
        y='UMAP2',
        # color='property_type',  # Color points based on property_type
        # color_discrete_map={prop_type: color for prop_type, color in zip(metadata['property_type'].unique(), color_scale)},
        hover_data=['image_url', 'price', 'bedrooms', 'bathrooms', 'latitude', 'longitude', 'property_type', 'lease', 'image_label']
    )

    fig.update_layout(
        plot_bgcolor=background_color,  # Set background color
        paper_bgcolor=background_color,  # Set plot area background color
        xaxis_title='',  # Hide x-axis label
        yaxis_title='',  # Hide y-axis label
        xaxis=dict(showticklabels=False),  # Hide x-ticks
        yaxis=dict(showticklabels=False),  # Hide y-ticks
    )

     # Customize point color
    for trace in fig.data:
        trace.marker.color = point_color

    image_url = ''  # Default: no image displayed
    if click_data:
        # Get the image URL from the clicked data point
        image_url = click_data['points'][0]['customdata'][0]
    
    # Update the image display and the plot
    return fig, image_url

if __name__ == '__main__':
    app.run_server(debug=True)
