from open_control import app
from open_control.utils import *
from flask import render_template, request, redirect, session, url_for
import io
import json
import os

@app.get('/')
def home():
    return render_template("home.html")



@app.post("/save_reactii_dropdowns")
def save_reactii_dropdowns():
    """
    Only used when submitting the form via the manual writing dropdowns
    :return:
    """
    save_reactions_file(request)
    return redirect(url_for('input_user'))

@app.post("/save_reactii_antimony")
def save_reactii_antimony():
    """
    Only used when submitting the form via the Antimony code textarea
    :return:
    """
    pass

@app.get('/input_user')
def input_user():
    """
    :return: The template with the inputs required to generate the graph, with all the file names
    that contain CNR's
    """
    files = sorted(os.listdir('open_control/templates/metode_lucru/'))
    temp = []
    for file in files:
        temp.append({'name': file})

    specii = session.get("specii")
    print('speciiles deja in sesiune:')
    print(specii)

    return render_template("input_user.html", data=temp)


@app.get('/crn_data')
def get_crn_data():
    """
    gets called by the input_user.html template with the filename, parses its data
    to find its species and how many reactions are in the CRN's, returning them back
    to the same template
    :return:
    """

    reactii_individuale : [str] = reactions_to_tellurium_format(request.args.get('filename'))

    specii, reacts = get_reaction_meta(session, reactii_individuale)
    data = {
             'speciiList' : specii,
             'reactsCount' : str(len(reacts)),
             }
    print("Speciile:")
    print(specii)
    print("reactiile")
    print(reacts)
    print("dictu de o sa se trimita")
    print(data)
    jsonu =json.dumps(data)
    print("jsonu de o sa se trimita")
    print(jsonu)
    return jsonu


@app.post('/input_user')
def input_user_post():
    """
    Saves the form data from the request to the current flask session
    including the "select"-ed file name
    start_time, end_time, titlu, x_titlu, y_titlu,
    the initial values of concentration for each species
    and the values for the reaction rates (the k's)

    :return: Redirects the user to '/graph' for displaying the graph generated
    """

    session['select'] = request.form.get('comp_select')

    session['start_time'] = request.form['start_time']

    session['end_time'] = request.form['end_time']

    session['titlu'] = request.form['titlu']

    session['x_titlu'] = request.form['x_titlu']

    session['y_titlu'] = request.form['y_titlu']


    #lista cu coeficientii pt fiecare specie
    valInitArray = []
    valInitIndex = 0

    while True:
        try:
            request_val_init = request.form['valinit' + str(valInitIndex)]
            valInitArray.append(str(request_val_init))
            valInitIndex += 1
        except:
            break

    const_array = []
    const_index = 0

    while True:
        try:
            request_const_init = request.form['valk' + str(const_index)]
            const_array.append(str(request_const_init))
            const_index += 1
        except:
            break

    session['init_vals'] = valInitArray
    session['react_constants'] = const_array

    print(session.get('end_time'))
    print(session.get('start_time'))
    print(session.get('titlu'))
    print(session.get('x_titlu'))
    print(session.get('y_titlu'))
    print(session.get('init_vals'))
    print(session.get('react_constants'))
    print(session.get('select'))
    print(session.get('specii'))

    return redirect(url_for('plot_svg'))

@app.get('/graph')
def plot_svg():
    """
    :return: Renders the graph front-end with the antimony code shown and stoichiometry matrix
    """
    [fig, listaToShow, stoichiometric_matrix] = create_figure(session)
    output = io.BytesIO()
    #    FigureCanvas(fig).print_png(output)
    #    return Response(output.getvalue(), mimetype='image/png')
    return render_template("graph.html", listaEcuatii=listaToShow, stoichMatrix=stoichiometric_matrix,
                           pageName="Chemical Reaction Network (CRN) - 2D")

