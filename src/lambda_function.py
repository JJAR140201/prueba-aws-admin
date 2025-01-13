import json
import boto3
import psycopg2
import os

# Configura las variables de entorno en Lambda para los valores sensibles
DB_HOST = os.getenv('DB_HOST', 'json-db.cbe8080uudt9.us-east-2.rds.amazonaws.com')
DB_NAME = os.getenv('DB_NAME', 'json-db')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '3218756308Juan_')
S3_BUCKET = os.getenv('S3_BUCKET', 'jj-bucket-prueba')

def lambda_handler(event, context):
    try:
        # Inicializar cliente S3
        s3 = boto3.client('s3')

        # Obtener información del archivo desde el evento
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']

        # Descargar el archivo desde S3
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        file_content = response['Body'].read().decode('utf-8')

        # Parsear el archivo JSON
        data = json.loads(file_content)

        # Conexión a la base de datos PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Procesar los datos y almacenarlos en la base de datos
        for record in data:
            # Consulta para insertar los datos en la tabla 'usuarios'
            query = """
                INSERT INTO usuarios (id, nombre, email, edad, pais)
                VALUES (%s, %s, %s, %s, %s)
            """
            # Extraer los valores del JSON
            values = (record['id'], record['nombre'], record['email'], record['edad'], record['pais'])
            cursor.execute(query, values)

        # Confirmar los cambios en la base de datos
        conn.commit()

        # Cerrar la conexión
        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps('Datos procesados y almacenados correctamente.')
        }

    except Exception as e:
        # Manejo de errores
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error procesando los datos: {str(e)}")
        }
