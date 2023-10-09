from flask import Blueprint, request, jsonify
from models.producto import Producto
import json
import validarToken as vt

ws_producto = Blueprint('ws_producto', __name__)

@ws_producto.route('/producto/catalogo', methods=['POST'])
@vt.validar
def catalogo():
    if request.method == 'POST':
        if 'categoria_id' not in request.form or 'almacen_id' not in request.form:
            return jsonify({'status': False, 'data': None, 'message': 'Falta parámetros'}), 400
        
        #Leer el parámetro de entrada
        categoria_id = request.form['categoria_id']
        almacen_id = request.form['almacen_id']

        #Instanciar a la clase Cliente
        obj = Producto()

        #Ejecutar al método catalogoCliente()
        resultadoJSON = obj.catalogo(categoria_id, almacen_id)

        #Convertir el resultado JSON(String) a JSON(Object)
        resultadoJSONObject = json.loads(resultadoJSON)

        if resultadoJSONObject['status'] == True:
            return jsonify(resultadoJSONObject), 200 #OK
        else:
            return jsonify(resultadoJSONObject), 205 #No content
