from flask import Blueprint, request, jsonify
from models.ciudad import Ciudad
import json
import validarToken as vt

ws_ciudad = Blueprint('ws_ciudad', __name__)

@ws_ciudad.route('/ciudad/listar', methods=['GET'])
@vt.validar
def listar():
    #Instanciar a la clase Cliente
    obj = Ciudad()

    #Ejecutar al método catalogoCliente()
    resultadoJSON = obj.listar()

    #Convertir el resultado JSON(String) a JSON(Object)
    resultadoJSONObject = json.loads(resultadoJSON)

    if resultadoJSONObject['status'] == True:
        return jsonify(resultadoJSONObject), 200 #OK
    else:
        return jsonify(resultadoJSONObject), 205 #No content

