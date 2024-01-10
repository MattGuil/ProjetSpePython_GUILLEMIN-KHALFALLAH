import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from Corpus import Corpus

app = dash.Dash(__name__)
app.title = 'Google'

app.layout = html.Div([
    dcc.Input(
        id='subject-input',
        value='Hydroponic',
        type='text',
        placeholder='Corpus :'
    ),
    dcc.Input(
        id='keywords-input',
        value='average,system',
        type='text',
        placeholder='Mots clés :'
    ),
    dcc.Slider(
        id='narticles-slider',
        min=2,
        max=100,
        step=2,
        value=10,
        marks={i: str(i) for i in range(0, 101, 10)}
    ),
    html.Button('Lancer la recherche', id='button'),
    html.Div(id='output')
])

@app.callback(
    Output('output', 'children'),
    Input('button', 'n_clicks'),
    Input('subject-input', 'value'),
    Input('keywords-input', 'value'),
    Input('narticles-slider', 'value')
)
def update_output(n_clicks, subject_value, keywords_value, narticles_value):
    if n_clicks is not None:
        corpus = Corpus(subject_value)
        corpus.fill(subject_value.lower(), narticles_value)
        corpus.search(subject_value)
        corpus.create_vocabulary()
        return corpus.vocab

if __name__ == '__main__':
    app.run_server(debug=True)
