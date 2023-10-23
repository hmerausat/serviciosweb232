from flask import Flask

#Importar a los módulos que contienen a los servicios web
from ws.sesion import ws_sesion
from ws.cliente import ws_cliente
from ws.venta import ws_venta
from ws.producto import ws_producto
from ws.ciudad import ws_ciudad

#Crear la variable de aplicación con Flask
app = Flask(__name__)


#Registrar los módulos que contienen a los servicios web
app.register_blueprint(ws_sesion)
app.register_blueprint(ws_cliente)
app.register_blueprint(ws_venta)
app.register_blueprint(ws_producto)
app.register_blueprint(ws_ciudad)

@app.route('/')
def home():
    return 'Los servicios web se encuentran en ejecución'

#Iniciar el servicio web con Flask
if __name__ == '__main__':
    app.run(port=81, debug=True, host='0.0.0.0')
