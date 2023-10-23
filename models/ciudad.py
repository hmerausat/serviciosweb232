from conexionBD import Conexion as db
import json

class Ciudad():
    def __init__(self, p_id=None, p_nombre=None):
        self.id = p_id
        self.nombre = p_nombre

    def listar(self):
        #Abrir la conexión a la BD
        con = db().open

        #Crear un cursor
        cursor = con.cursor()

        #Preparar la sentencia SQL
        sql = """
            select * from ciudad order by 2
            """
        
        #Ejecutar la sentencia
        cursor.execute(sql)
        
        #Recuperar los datos y almacenarlos en la variable "datos"
        datos = cursor.fetchall()

        #Cerrar el cursor y la conexión
        cursor.close()
        con.close()

        #Retornar los resultados
        if datos:
            return json.dumps({'status': True, 'data': datos, 'message': 'Lista de ciudades'})
        else:
            return json.dumps({'status': False, 'data': [], 'message': 'Sin registros'})

    