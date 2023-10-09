from conexionBD import Conexion as db
import json
from util import CustomJsonEncoder

class Venta():
    def __init__(self, cliente_id=None, tipo_comprobante_id=None, nser=None, fdoc=None, usuario_id_registro=None, almacen_id=None, detalle_venta=None):
        self.cliente_id = cliente_id
        self.tipo_comprobante_id = tipo_comprobante_id
        self.nser = nser
        self.fdoc = fdoc
        self.usuario_id_registro = usuario_id_registro
        self.almacen_id = almacen_id
        self.detalle_venta = detalle_venta

    def registrar(self):
        #Abrir conexión a la BD
        con = db().open

        #Configurar para que los cambios de escritura en la BD se confirmen de manera manual
        con.autocommit = False

        #Crear un cursor
        cursor = con.cursor()

        try:
            #Transacción para registrar una venta

            #1:Generar el número de comprobante, en función al tipo de comprobante y la serie
            sql = "select ndoc+1 as numero_comprobante from serie where tipo_comprobante_id=%s and serie=%s"
            cursor.execute(sql, [self.tipo_comprobante_id, self.nser])
            datos = cursor.fetchone()
            numero_comprobante = datos['numero_comprobante']

            #2:Insertar en la tabla venta
            sql = """
                    insert into venta
                        (
                            cliente_id, 
                            tipo_comprobante_id, 
                            nser,
                            ndoc,
                            fdoc,
                            sub_total,
                            igv,
                            total,
                            porcentaje_igv,
                            usuario_id_registro,
                            almacen_id
                        )
                        values
                        (
                            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                        )
                """
            cursor.execute(sql, [self.cliente_id, self.tipo_comprobante_id, self.nser, numero_comprobante, self.fdoc, 0, 0, 0, 18, self.usuario_id_registro, self.almacen_id])

            #3: Insertar en la tabla venta_detalle (preparar la sentencia)
            sql = "insert into venta_detalle(venta_id, producto_id, cantidad, precio, importe) values (%s,%s,%s,%s,%s)"

            #Obtener el ID de la venta que se acaba de registrar
            venta_id = con.insert_id()

            #Recoger los datos del producto_id, cantidad y precio para el detalle de la venta. Dichos datos vienen en formato de JSON Array
            detalleVentaJSONArray = json.loads(self.detalle_venta)

            #Recorrer cada elemento del JSON Array
            sub_total = 0
            igv = 0
            total = 0
            for producto in detalleVentaJSONArray:
                #Por cada elemento del JSON Array debemos capturar los datos del producto: producto_id, cantidad, precio
                producto_id = producto["producto_id"]
                cantidad = producto["cantidad"]
                precio = producto["precio"]
                importe = float(cantidad) * float(precio)
                total = total + importe

                #Validar el stock disponible de cada producto. 
                #Si la cantidad de venta supera al stock disponible, se debe mostrar un mensaje de error
                sql_validar_stock = """
                                        select 
                                            s.stock, 
                                            p.nombre as producto
                                        from 
                                            stock_almacen s 
                                            inner join producto p on (s.producto_id = p.id) 
                                        where 
                                            s.producto_id=%s and s.almacen_id=%s
                                    """
                cursor.execute(sql_validar_stock, [producto_id, self.almacen_id])
                datos_stock_producto = cursor.fetchone()
                stock_actual = datos_stock_producto["stock"]
                nombre_producto = datos_stock_producto["producto"]
                
                if int(cantidad) > stock_actual:
                    return json.dumps({'status': False, 'data':None, 'message': 'Stock insuficiente en el producto: ' + nombre_producto})

                #Ejecutar la sentencia para insertar en la tabla venta_detalle
                cursor.execute(sql, [venta_id, producto_id, cantidad, precio, importe])

                #4: Por cada producto que se vende, debo descontar el stock
                sql_actualizar_stock = "update stock_almacen set stock = stock - %s where producto_id = %s and almacen_id = %s"
                cursor.execute(sql_actualizar_stock, [cantidad, producto_id, self.almacen_id])

                #Fin del bucle "for"
            
            #5: Actualizar el número de comprobante utilizado en la tabla "serie"
            sql = "update serie set ndoc = %s where serie = %s"
            cursor.execute(sql, [numero_comprobante, self.nser])

            #6: Actualizar los totales de la venta
            sql = "update venta set sub_total=%s, igv=%s, total=%s where id=%s"
            sub_total = total / 1.18
            igv = total - sub_total
            cursor.execute(sql, [sub_total, igv, total, venta_id])

            #7: Confirmar la transacción de venta
            con.commit()

            #Retornar un mensaje
            return json.dumps({'status': True, 'data': {'venta_id': venta_id, 'tipo_comprobante_id': self.tipo_comprobante_id, 'serie': self.nser, 'ndoc': numero_comprobante}, 'message': 'Venta registrada correctamente'})

        except con.Error as error:
            #Revocar la operación en la base de datos
            con.rollback()

            return json.dumps({'status': False, 'data': None, 'message': format(error)})
        finally:
            cursor.close()
            con.close()

    def listar(self, id):
        #Abrir la conexión a la BD
        con = db().open

        #Crear un cursor
        cursor = con.cursor()

        #Preparar la sentencia SQL
        if id == 0:
            sql =   """
                        select 
                            v.*, 
                            c.nombre as cliente 
                        from 
                            venta v inner join cliente c on (v.cliente_id = c.id) 
                        order by 
                            id desc
                    """
            #Ejecutar la sentencia
            cursor.execute(sql)
        else:
            sql =   """
                        select 
                            v.*, 
                            c.nombre as cliente 
                        from 
                            venta v inner join cliente c on (v.cliente_id = c.id)   
                        where 
                            v.id = %s
                    """
            #Ejecutar la sentencia
            cursor.execute(sql, [id])
        
        #Recuperar los datos y almacenarlos en la variable "datos"
        ventas = cursor.fetchall()

        #Declarar una variable para preparar el resultado
        resultado = [] #Array
        for venta in ventas:
            cliente = venta["cliente"]
            venta_id = venta["id"]
            tipo_comprobante_id = venta["tipo_comprobante_id"]
            nser = venta["nser"]
            ndoc = venta["ndoc"]
            fdoc = venta["fdoc"]
            sub_total = venta["sub_total"]
            igv = venta["igv"]
            total = venta["total"]
            cliente_id = venta["cliente_id"]

            sql_detalle_venta = """
                                    select 
                                        d.producto_id, 
                                        d.cantidad, 
                                        d.precio, 
                                        d.importe, 
                                        p.nombre as producto 
                                    from 
                                        venta_detalle d 
                                        inner join producto p on (d.producto_id = p.id) 
                                        where venta_id = %s
                                """
            cursor.execute(sql_detalle_venta, [venta_id])
            detalle_venta = cursor.fetchall()
            detalle_venta = [{'producto': detalle['producto'], 'producto_id': detalle['producto_id'], 'cantidad': detalle['cantidad'], 'precio': detalle['precio'], 'importe': detalle['importe']} for detalle in detalle_venta ]
            resultado.append(
                {
                    'cliente': cliente,
                    'venta_id': venta_id,
                    'tipo_comprobante_id': tipo_comprobante_id,
                    'nser': nser,
                    'ndoc': ndoc,
                    'fdoc': fdoc,
                    'sub_total': sub_total,
                    'igv': igv,
                    'total': total,
                    'cliente_id': cliente_id,
                    'venta_productos': detalle_venta
                }
            )

        #Cerrar el cursor y la conexión
        cursor.close()
        con.close()

        #Retornar los resultados
        if ventas:
            return json.dumps({'status': True, 'data': resultado, 'message': 'Lista de ventas'}, cls=CustomJsonEncoder)
        else:
            return json.dumps({'status': False, 'data': [], 'message': 'Sin registros'})
