# Solución de problemas comunes en AWS

## Problema 1: Una instancia EC2 no puede conectarse a Internet

### Posibles causas y soluciones:

#### 1. La instancia no tiene una dirección IP pública:
Muchas veces, el problema ocurre porque la instancia no tiene asignada una IP pública. Para verificarlo, ve a la consola de **EC2**, busca tu instancia y revisa si tiene una IP pública en la columna correspondiente. 

- **Solución**: Si no tiene una IP pública:
  1. Ve a **Elastic IPs** en la consola de EC2.
  2. Asigna una nueva Elastic IP a tu instancia.

#### 2. El grupo de seguridad no permite tráfico saliente (outbound):
A veces, el grupo de seguridad bloquea el tráfico saliente. Para solucionarlo:
1. Ve al grupo de seguridad asociado a tu instancia.
2. Asegúrate de que permita el tráfico saliente a **0.0.0.0/0** en los puertos **80 (HTTP)** y **443 (HTTPS)**.

- **Solución**: Agrega una regla como esta:
    ```
    Tipo: All traffic
    Protocolo: All
    Rango de puertos: All
    Destino: 0.0.0.0/0
    ```

#### 3. La instancia no está en una Subnet con una Gateway de Internet:
Si la instancia está en una subnet que no tiene una Gateway de Internet asociada, no podrá acceder a Internet.

- **Solución**: Ve a la consola de **VPC**, verifica si la subnet tiene una tabla de rutas asociada con una Internet Gateway. Si no es así:
  1. Configura una **Internet Gateway** y asóciala a tu VPC.
  2. Modifica la tabla de rutas para que incluya:
     ```
     Destino: 0.0.0.0/0
     Target: Internet Gateway
     ```

#### 4. Firewall local en la instancia:
Si todo lo anterior está configurado correctamente, revisa las reglas del firewall dentro de la instancia (como `iptables`).

- **Solución**: Asegúrate de que permita tráfico saliente.

---

## Problema 2: Un bucket S3 configurado para acceso público devuelve un error 403

### Posibles causas y soluciones:

#### 1. La política del bucket no permite acceso público:
Este es un problema común. Ve a la consola de **S3**, revisa la pestaña **Permissions** y verifica la política del bucket.

- **Solución**: Usa una política similar a esta, reemplazando `<bucket-name>` con el nombre de tu bucket:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::<bucket-name>/*"
            }
        ]
    }
    ```

#### 2. El Bloqueo de Acceso Público está activado:
A veces, el acceso público está bloqueado en la configuración del bucket. Para solucionarlo:
1. Ve a la pestaña **Permissions** en la consola de S3.
2. Desactiva la opción **"Block all public access"** si está habilitada.

#### 3. La ACL del objeto no permite acceso público:
Si todo lo anterior está bien configurado, verifica las ACLs del objeto específico. Ve a la consola de S3, selecciona un archivo y revisa sus permisos en **Access control list (ACL)**.

- **Solución**: Asegúrate de que el archivo tenga permisos de lectura pública.

#### 4. Configuración de endpoint privado:
Si el bucket está asociado a un endpoint de VPC, puede interferir con el acceso público.

- **Solución**: Ajusta las políticas de acceso para permitir solicitudes externas.

---

## Problema 3: Una función Lambda tarda demasiado en ejecutarse

### Posibles causas y soluciones:

#### 1. Problemas de red (latencia alta):
Si la función Lambda accede a recursos externos como RDS, API o S3, puede haber latencia en las conexiones.

- **Solución**: 
  - Asegúrate de que Lambda esté en la misma región que los recursos.
  - Configura Lambda en la misma VPC que los recursos que está utilizando.

#### 2. Configuración inadecuada de memoria:
Lambda asigna más CPU cuando se le configura más memoria.

- **Solución**: Incrementa la memoria asignada a la función Lambda desde la consola.

#### 3. Código no optimizado:
El código puede estar procesando datos innecesariamente lento o con demasiados bucles.

- **Solución**:
  - Optimiza el código.
  - Usa **batch processing** si estás procesando múltiples objetos.
  - Reutiliza conexiones persistentes, como a bases de datos.

#### 4. Cold starts (inicio en frío):
Si Lambda no se ha ejecutado recientemente, puede tardar más en inicializarse.

- **Solución**: Usa **Provisioned Concurrency** para mantener la función "caliente".

#### 5. Retrasos al consultar RDS:
Si Lambda tarda en conectarse a la base de datos RDS, el problema podría estar en el manejo de conexiones.

- **Solución**: Usa un pool de conexiones en Lambda y verifica que RDS esté configurado para aceptar múltiples conexiones simultáneas.

#### 6. Errores silenciosos:
Si hay errores en el código que no se capturan, Lambda puede parecer más lento.

- **Solución**: Agrega logs en puntos clave para rastrear problemas.
