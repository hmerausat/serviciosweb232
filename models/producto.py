from conexionBD import Conexion as db
import json
from util import CustomJsonEncoder

class Producto():
    def __init__(self, nombre=None, precio=None, categoria_id=None):
        self.nombre = nombre
        self.precio = precio
        self.categoria_id = categoria_id
    
    def catalogo(self, categoria_id, almacen_id):
        #Abrir la conexión a la BD
        con = db().open

        #Crear un cursor
        cursor = con.cursor()

        #Preparar la sentencia SQL
        sql = """
            select 
                p.id,
                p.nombre,
                p.precio,
                c.nombre as categoria,
                s.stock,
                concat('/static/imgs-producto/', p.id, '.jpg') as foto
            from
                producto p 
                inner join categoria c on (p.categoria_id = c.id)
                inner join stock_almacen s on ( p.id = s.producto_id )

            where
                (case when %s=0 then TRUE else p.categoria_id=%s end)
                and s.almacen_id = %s
            order by
                2
            """
        
        #Ejecutar la sentencia
        cursor.execute(sql, [categoria_id, categoria_id, almacen_id])
        
        #Recuperar los datos y almacenarlos en la variable "datos"
        datos = cursor.fetchall()

        #Cerrar el cursor y la conexión
        cursor.close()
        con.close()

        #Retornar los resultados
        if datos:
            return json.dumps({'status': True, 'data': datos, 'message': 'Lista de productos'}, cls=CustomJsonEncoder)
        else:
            return json.dumps({'status': False, 'data': [], 'message': 'Sin registros'})

        