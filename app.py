from flask import Flask, url_for, render_template, request, redirect
from markupsafe import escape
import mysql.connector
from flask_mail import Mail, Message
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

#Conexion a mi capa de datos
bdd_connection = mysql.connector.connect(
    host = '3.91.222.78',
    user= 'adminBDD',
    password='adminBDD23-1',
    database='trabajoSObdd'
)
bdd = bdd_connection.cursor()

# Función para obtener el valor actual del tipo de cambio interbancario.
def obtener_tipo_cambio(classhtml, numlist):
    URL = 'https://cuantoestaeldolar.pe/'
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    tipo_de_cambio_elements = soup.find_all('p', class_=classhtml)
    tipo_de_cambio_element = tipo_de_cambio_elements[numlist]
    tipo_de_cambio = tipo_de_cambio_element.text
    return tipo_de_cambio

def update_tipo_cambio():
    j = 1
    for i in range(10):
        if(i%2==0 and i != 0):
            j+=1
        if (i%2==0):
            valor = obtener_tipo_cambio('text-2xl md:w-40 flex justify-center', i)
            bdd.execute(('UPDATE Negocio SET precio_venta = %s WHERE id_negocio = %s'), (valor, str(j),))
        else:
            valor = obtener_tipo_cambio('text-2xl md:w-40 flex justify-center', i)
            bdd.execute(('UPDATE Negocio SET precio_compra = %s WHERE id_negocio = %s'), (valor, str(j),))
        
        bdd_connection.commit()



@app.route('/')
def nombre_negocio():
    bdd.execute('SELECT nombre_negocio, precio_compra, precio_venta FROM Negocio')
    table = bdd.fetchall()
    update_tipo_cambio()
    return render_template("index.html", table=table)
#-------------------------------------------------------------------
#Flask mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'tukambioupc@gmail.com'
app.config['MAIL_PASSWORD'] = 'ktsbqhwxpncsmplr'
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
            bdd.execute(('INSERT INTO Alerta (id_tipo_operacion, correo, valor_deseado) VALUES (%s, %s, %s)'), (1, correo, cantidad,))
            if(c):
                msg.body = '¡El valor del dolar (precio de compra) ha llegado al deseado en la entidad ingresada!'
                email.send(msg)
        elif op == 'precio_venta':
            bdd.execute(('SELECT precio_venta FROM Negocio WHERE precio_venta  = %s  AND nombre_negocio = %s'), (cantidad, entidad,))
            c = bdd.fetchone()
            bdd.execute(('INSERT INTO Alerta (id_tipo_operacion, correo, valor_deseado) VALUES (%s, %s, %s)'), (2, correo, cantidad,))
            if(c):
                msg.body = '¡El valor del dolar (precio de venta) ha llegado al deseado en la entidad ingresada!'
                email.send(msg)

    return redirect(url_for('nombre_negocio'))
#-------------------------------------------------------------------

