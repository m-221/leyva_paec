from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)

app.secret_key = '32423j'


# =============================================
# FUNCIÓN PARA CONECTAR A MYSQL
# =============================================

def conectar():

    return mysql.connector.connect(

        host="localhost",
        user="root",
        password="",
        database="salud",
        port=3306
    )


# =============================================
# CREAR BASE DE DATOS Y TABLA
# =============================================

def crear_base_datos():

    conexion = mysql.connector.connect(

        host="localhost",
        user="root",
        password="",
        port=3306
    )

    cursor = conexion.cursor()

    # =============================================
    # CREAR BASE DE DATOS
    # =============================================

    cursor.execute("CREATE DATABASE IF NOT EXISTS salud")

    cursor.execute("USE salud")

    # =============================================
    # CREAR TABLA
    # =============================================

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS registros_imc (

            id INT AUTO_INCREMENT PRIMARY KEY,

            nombre VARCHAR(100) NOT NULL,

            peso DECIMAL(6,2) NOT NULL,

            altura DECIMAL(4,2) NOT NULL,

            imc DECIMAL(5,2) NOT NULL,

            categoria VARCHAR(100) NOT NULL,

            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )

    """)

    # =============================================
    # AGREGAR EDAD SI NO EXISTE
    # =============================================

    cursor.execute("SHOW COLUMNS FROM registros_imc LIKE 'edad'")

    existe_edad = cursor.fetchone()

    if not existe_edad:

        cursor.execute("""

            ALTER TABLE registros_imc

            ADD COLUMN edad INT NOT NULL DEFAULT 0 AFTER nombre

        """)

    # =============================================
    # AGREGAR GÉNERO SI NO EXISTE
    # =============================================

    cursor.execute("SHOW COLUMNS FROM registros_imc LIKE 'genero'")

    existe_genero = cursor.fetchone()

    if not existe_genero:

        cursor.execute("""

            ALTER TABLE registros_imc

            ADD COLUMN genero VARCHAR(20) NOT NULL DEFAULT 'hombre' AFTER edad

        """)

    conexion.commit()

    cursor.close()

    conexion.close()


# =============================================
# PORTADA
# =============================================

@app.route('/')
def main():

    return render_template('portada.html')


# =============================================
# INICIO
# =============================================

@app.route("/inicio")
def principal():

    return render_template("inicio.html")


# =============================================
# HISTORIA
# =============================================

@app.route("/historia")
def historia():

    return render_template("historia.html")


# =============================================
# QUÍMICA
# =============================================

@app.route("/quimica")
def quimica():

    return render_template("quimica.html")


# =============================================
# CALCULADORA IMC
# =============================================

@app.route('/imc', methods=['GET', 'POST'])
def imc():

    resultado = None

    categoria = None

    nombre = None

    edad = None

    genero = None

    error = None

    recomendacion = None

    alimentacion = None

    ejercicios = None

    beneficios = None

    imagen_figura = None

    porcentaje_grafica = 0

    menor_edad = False

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    # =============================================
    # SI EL USUARIO ENVÍA EL FORMULARIO
    # =============================================

    if request.method == 'POST':

        try:

            nombre = request.form.get('nombre')

            edad = int(request.form.get('edad'))

            genero = request.form.get('genero')

            peso = float(request.form.get('peso'))

            altura = float(request.form.get('altura'))

            # =============================================
            # VALIDACIONES
            # =============================================

            if nombre == "" or genero == "":

                error = "Debes llenar todos los campos."

            elif edad <= 0 or edad > 120:

                error = "La edad no es válida."

            elif peso <= 0 or peso > 400:

                error = "El peso no es válido."

            elif altura <= 0 or altura > 2.50:

                error = "La altura no es válida. Usa metros, ejemplo 1.70."

            else:

                # =============================================
                # CALCULAR IMC
                # =============================================

                resultado = peso / (altura * altura)

                resultado = round(resultado, 2)

                menor_edad = edad < 18

                # =============================================
                # CLASIFICAR IMC
                # =============================================

                if resultado < 18.5:

                    categoria = "Bajo peso"

                    clave_img = "bajo_peso"

                    alimentacion = "Aumentar alimentos nutritivos como huevo, pollo, arroz, avena y frutas."

                    ejercicios = "Ejercicios ligeros y caminatas."

                    recomendacion = "Tu IMC indica bajo peso."

                elif resultado < 25:

                    categoria = "Peso normal o saludable"

                    clave_img = "normal"

                    alimentacion = "Mantener una alimentación balanceada."

                    ejercicios = "Caminar, correr suave y hacer deporte."

                    recomendacion = "Tu IMC está en un rango saludable."

                elif resultado < 30:

                    categoria = "Sobrepeso"

                    clave_img = "sobrepeso"

                    alimentacion = "Reducir refrescos y comida rápida."

                    ejercicios = "Caminar y hacer actividad física frecuente."

                    recomendacion = "Tu IMC indica sobrepeso."

                elif resultado < 35:

                    categoria = "Obesidad grado I"

                    clave_img = "obesidad1"

                    alimentacion = "Evitar azúcar y comida grasosa."

                    ejercicios = "Ejercicios de bajo impacto."

                    recomendacion = "Tu IMC indica obesidad grado I."

                elif resultado < 40:

                    categoria = "Obesidad grado II"

                    clave_img = "obesidad2"

                    alimentacion = "Controlar porciones y bebidas azucaradas."

                    ejercicios = "Caminar y bicicleta."

                    recomendacion = "Tu IMC indica obesidad grado II."

                else:

                    categoria = "Obesidad grado III u obesidad mórbida"

                    clave_img = "obesidad3"

                    alimentacion = "Seguir un plan alimenticio supervisado."

                    ejercicios = "Actividad física suave."

                    recomendacion = "Tu IMC indica obesidad grado III."

                # =============================================
                # BENEFICIOS
                # =============================================

                beneficios = "Una vida saludable ayuda a prevenir enfermedades."

                # =============================================
                # IMAGEN
                # =============================================

                if menor_edad:

                    imagen_figura = "img/menor.png"

                else:

                    imagen_figura = "img/" + clave_img + "_" + genero + ".png"

                # =============================================
                # PORCENTAJE PARA LA BARRA
                # =============================================

                porcentaje_grafica = round((resultado / 45) * 100, 2)

                if porcentaje_grafica > 100:

                    porcentaje_grafica = 100

                # =============================================
                # GUARDAR EN MYSQL
                # =============================================

                cursor.execute("""

                    INSERT INTO registros_imc

                    (nombre, edad, genero, peso, altura, imc, categoria)

                    VALUES (%s, %s, %s, %s, %s, %s, %s)

                """, (

                    nombre,
                    edad,
                    genero,
                    peso,
                    altura,
                    resultado,
                    categoria

                ))

                conexion.commit()

        except ValueError:

            error = "Revisa los datos. Peso, altura y edad deben ser números."

    # =============================================
    # OBTENER REGISTROS
    # =============================================

    cursor.execute("SELECT * FROM registros_imc ORDER BY id DESC")

    registros = cursor.fetchall()

    cursor.close()

    conexion.close()

    # =============================================
    # ENVIAR DATOS AL HTML
    # =============================================

    return render_template(

        'imc.html',

        nombre=nombre,

        edad=edad,

        genero=genero,

        resultado=resultado,

        categoria=categoria,

        error=error,

        recomendacion=recomendacion,

        alimentacion=alimentacion,

        ejercicios=ejercicios,

        beneficios=beneficios,

        imagen_figura=imagen_figura,

        porcentaje_grafica=porcentaje_grafica,

        menor_edad=menor_edad,

        registros=registros
    )


# =============================================
# ESTADÍSTICAS GENERALES
# =============================================

@app.route("/estadisticas")
def estadisticas():

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    # =============================================
    # OBTENER TODOS LOS REGISTROS
    # =============================================

    cursor.execute("SELECT * FROM registros_imc")

    registros = cursor.fetchall()

    total = len(registros)

    # =============================================
    # CONTADORES
    # =============================================

    bajo = 0

    normal = 0

    sobrepeso = 0

    obesidad = 0

    hombres = 0

    mujeres = 0

    suma_imc = 0

    # =============================================
    # RECORRER REGISTROS
    # =============================================

    for r in registros:

        categoria = r["categoria"]

        genero = r["genero"]

        imc = float(r["imc"])

        suma_imc += imc

        # =============================================
        # CONTAR CATEGORÍAS
        # =============================================

        if "Bajo" in categoria:

            bajo += 1

        elif "normal" in categoria.lower():

            normal += 1

        elif "Sobrepeso" in categoria:

            sobrepeso += 1

        elif "Obesidad" in categoria:

            obesidad += 1

        # =============================================
        # CONTAR GÉNERO
        # =============================================

        if genero == "hombre":

            hombres += 1

        elif genero == "mujer":

            mujeres += 1

    # =============================================
    # CALCULAR PORCENTAJES
    # =============================================

    if total > 0:

        p_bajo = round((bajo / total) * 100, 2)

        p_normal = round((normal / total) * 100, 2)

        p_sobrepeso = round((sobrepeso / total) * 100, 2)

        p_obesidad = round((obesidad / total) * 100, 2)

        promedio_imc = round(suma_imc / total, 2)

    else:

        p_bajo = 0

        p_normal = 0

        p_sobrepeso = 0

        p_obesidad = 0

        promedio_imc = 0

    # =============================================
    # MENSAJE AUTOMÁTICO
    # =============================================

    mensaje = ""

    if p_obesidad >= 50:

        mensaje = "La mayoría de las personas registradas presentan obesidad."

    elif p_normal >= 50:

        mensaje = "La mayoría de las personas tienen un peso saludable."

    elif p_sobrepeso >= 50:

        mensaje = "Gran parte de las personas presentan sobrepeso."

    else:

        mensaje = "Los resultados están distribuidos entre varias categorías."

    cursor.close()

    conexion.close()

    # =============================================
    # ENVIAR DATOS AL HTML
    # =============================================

    return render_template(

        "estadisticas.html",

        total=total,

        promedio_imc=promedio_imc,

        hombres=hombres,

        mujeres=mujeres,

        p_bajo=p_bajo,

        p_normal=p_normal,

        p_sobrepeso=p_sobrepeso,

        p_obesidad=p_obesidad,

        mensaje=mensaje
    )


# =============================================
# EDITAR REGISTRO
# =============================================

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    conexion = conectar()

    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':

        nombre = request.form.get('nombre')

        peso = float(request.form.get('peso'))

        altura = float(request.form.get('altura'))

        # =============================================
        # RECALCULAR IMC
        # =============================================

        imc = peso / (altura * altura)

        imc = round(imc, 2)

        # =============================================
        # CATEGORÍA
        # =============================================

        if imc < 18.5:

            categoria = "Bajo peso"

        elif imc < 25:

            categoria = "Peso normal"

        elif imc < 30:

            categoria = "Sobrepeso"

        else:

            categoria = "Obesidad"

        # =============================================
        # ACTUALIZAR REGISTRO
        # =============================================

        cursor.execute("""

            UPDATE registros_imc

            SET nombre=%s, peso=%s, altura=%s, imc=%s, categoria=%s

            WHERE id=%s

        """, (

            nombre,
            peso,
            altura,
            imc,
            categoria,
            id

        ))

        conexion.commit()

        cursor.close()

        conexion.close()

        return redirect(url_for('imc'))

    # =============================================
    # OBTENER REGISTRO
    # =============================================

    cursor.execute("SELECT * FROM registros_imc WHERE id=%s", (id,))

    registro = cursor.fetchone()

    cursor.close()

    conexion.close()

    return render_template('editar_imc.html', registro=registro)


# =============================================
# BORRAR REGISTRO
# =============================================

@app.route('/borrar/<int:id>')
def borrar(id):

    conexion = conectar()

    cursor = conexion.cursor()

    cursor.execute("DELETE FROM registros_imc WHERE id=%s", (id,))

    conexion.commit()

    cursor.close()

    conexion.close()

    return redirect(url_for('imc'))


# =============================================
# INICIAR APP
# =============================================

if __name__ == "__main__":

    crear_base_datos()

    app.run(debug=True)