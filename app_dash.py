import dash
from dash import dcc, html
from dash.dependencies import Input, Output

from Corpus import Corpus

# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = 'KHALMIN SEARCH ENGINE'

# Styles CSS pour l'application
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
    # Styles pour les champs de saisie et le bouton
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

# Création de la mise en page de l'application
app.layout = html.Div([
    html.H1('KHALMIN SEARCH ENGINE', id="title", style=styles['title']),
    html.Div([
        # Champs de saisie du sujet du corpus
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
        # Champs de saisie des mots clés
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
        # Slider pour sélectionner le nombre d'articles
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
        # Bouton pour lancer la recherche
        html.Button('Lancer la recherche', id='button', style=styles['button']),
    ], id='form', style=styles['form']),
    # Div pour afficher les résultats de la recherche
    html.Div(id='output', style=styles['output'])
], style=styles['body'])

# Callback pour mettre à jour les résultats de la recherche
@app.callback(
    Output('output', 'children'),
    [Input('button', 'n_clicks')],
    Input('subject-input', 'value'),
    Input('keywords-input', 'value'),
    Input('narticles-slider', 'value'),
    prevent_initial_call=True
)
def update_output(n_clicks, subject_value, keywords_value, narticles_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        # Aucun déclencheur, retourner une valeur par défaut ou un message
        return html.Div("Cliquez sur le bouton pour afficher les résultats.")
    else:
        # Une entrée a été déclenchée, récupérez les valeurs des inputs
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id == 'button' and n_clicks:
            print(subject_value)
            print(keywords_value)
            print(narticles_value)
            corpus = Corpus(subject_value)
            corpus.fill(subject_value.lower(), narticles_value)
            corpus.search(subject_value)
            corpus.create_vocabulary()
            similarity_results = corpus.compute_similarity(keywords_value)
            
            result_display = []

            # Création des éléments HTML pour afficher les résultats
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
    # Lancement de l'application
    app.run_server(debug=True, port=8000, threaded=True)
