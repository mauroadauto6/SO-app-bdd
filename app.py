from flask import Flask, url_for, render_template, request, redirect
from markupsafe import escape
import mysql.connector
from flask_mail import Mail, Message

app = Flask(__name__)

#Conexion a mi capa de datos
bdd_connection = mysql.connector.connect(
    host = '44.204.74.23',
    user= 'adminBDD',
    password='adminBDD23-1',
    database='trabajoSObdd'
)
bdd = bdd_connection.cursor()


@app.route('/')
def nombre_negocio():
    bdd.execute('SELECT nombre_negocio, precio_compra, precio_venta FROM Negocio')
    table = bdd.fetchall()
    return render_template("index.html", table=table)

#-------------------------------------------------------------------
#Flask mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'tukambioupc@gmail.com'
app.config['MAIL_PASSWORD'] = 'iuvydzwwagisolal'
email = Mail(app)

@app.route('/form-ok', methods=['GET', 'POST'])
def notificacion_correo():
    #datos de los input
    if request.method == 'POST':
        op = request.form['flexRadioDefault']
        cantidad = request.form['cantidad']
        entidad = request.form['entidad']
        correo = request.form['correo']

        msg = Message('Coincidencia detectada', sender='tukambioupc@gmail.com', recipients=[correo])

        if op == 'precio_compra':
            bdd.execute(('SELECT precio_compra FROM Negocio WHERE precio_compra = %s  AND nombre_negocio = %s'), (cantidad, entidad,))
            c = bdd.fetchone()
            if(c):
                msg.body = '¡El valor del dolar (precio de compra) ha llegado al deseado en la entidad ingresada!'
                email.send(msg)
        elif op == 'precio_venta':
            bdd.execute(('SELECT precio_venta FROM Negocio WHERE precio_venta  = %s  AND nombre_negocio = %s'), (cantidad, entidad,))
            c = bdd.fetchone()
            if(c):
                msg.body = '¡El valor del dolar (precio de venta) ha llegado al deseado en la entidad ingresada!'
                email.send(msg)

    return redirect(url_for('nombre_negocio'))
