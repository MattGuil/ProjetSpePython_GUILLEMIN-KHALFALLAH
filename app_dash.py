import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from Corpus import Corpus

app = dash.Dash(__name__)
app.title = 'KHALMIN SEARCH ENGINE'

styles = {
    'body': {
        'fontFamily': 'Arial, sans-serif'
    },
    'title': {
        'textAlign': 'center'
    },
    'form': {
        'textAlign': 'center',
        'display': 'flex',
        'flexDirection': 'column'
    },
    'input-div': {
        'display': 'flex',
        'flexDirection': 'column',
        'margin': '20px'
    },
    'input_fields': {
        'width': '50%',
        'margin': '10px auto',
        'textAlign': 'center'
    },
    'button': {
        'margin': '10px auto'
    },
    'output': {
        'margin': '20px'
    },
    'result': {
        'border': '1px solid black',
        'padding': '10px',
        'margin': '10px'
    }
}

app.layout = html.Div([
    html.H1('KHALMIN SEARCH ENGINE', id="title", style=styles['title']),
    html.Div([
        html.Div([
            html.Label('Sujet du Corpus', className='label'),
            dcc.Input(
                id='subject-input',
                value='Hydroponic',
                type='text',
                placeholder='Sujet du Corpus',
                style=styles['input_fields']
            ),
        ], style=styles['input-div']),
        html.Div([
            html.Label('Mots clés', className='label'),
            dcc.Input(
                id='keywords-input',
                value='average,system',
                type='text',
                placeholder='Mots clés',
                style=styles['input_fields']
            ),
        ], style=styles['input-div']),
        html.Div([
            html.Label('Nombre d\'articles', className='label'),
            html.Div(
                dcc.Slider(
                    id='narticles-slider',
                    min=2,
                    max=100,
                    step=2,
                    value=10,
                    marks={i: str(i) for i in range(0, 101, 10)}
                ),
                style=styles['input_fields']
            ),
        ], style=styles['input-div']),
        html.Button('Lancer la recherche', id='button', style=styles['button']),
    ], id='form', style=styles['form']),
    html.Div(id='output', style=styles['output'])
], style=styles['body'])

@app.callback(
    Output('output', 'children'),
    [Input('button', 'n_clicks')],
    prevent_initial_call=True
)
def update_output(n_clicks):
    if n_clicks:
        subject_value = app.layout['subject-input'].value
        keywords_value = app.layout['keywords-input'].value
        narticles_value = app.layout['narticles-slider'].value
        
        if subject_value and keywords_value and narticles_value:
            corpus = Corpus(subject_value)
            corpus.fill(subject_value.lower(), narticles_value)
            corpus.search(subject_value)
            corpus.create_vocabulary()
            similarity_results = corpus.compute_similarity(keywords_value)
            
            result_display = []

            for result in similarity_results:
                if result[0].origine == "Reddit":
                    result_display.append(
                        html.Div([
                            html.P(f"Titre : {result[0].titre}"),
                            html.P(f"Auteur : {result[0].auteur}"),
                            html.P(f"Date : {result[0].date}"),
                            html.P(f"URL : {result[0].url}"),
                            html.P(f"Nombre de commentaires : {result[0].get_nbcom()}"),
                            html.P("\n"),
                            html.P(f"Similarité : {result[1]}")
                        ], className='result', style=styles['result'])
                    )
                else:
                    result_display.append(
                        html.Div([
                            html.P(f"Titre : {result[0].titre}"),
                            html.P(f"Auteur(s) : {result[0].auteurs}"),
                            html.P(f"Date : {result[0].date}"),
                            html.P(f"URL : {result[0].url}"),
                            html.P("\n"),
                            html.P(f"Similarité : {result[1]}")
                        ], className='result', style=styles['result'])
                    )
            
            return result_display

if __name__ == '__main__':
    app.run_server(debug=True, port=8000, threaded=True)
