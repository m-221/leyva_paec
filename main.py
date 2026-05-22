from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '32423j'


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="salud",
        port=3306
    )
def crear_base_datos():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        port=3306
    )

    cursor = conexion.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS salud")
    cursor.execute("USE salud")

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

    cursor.execute("SHOW COLUMNS FROM registros_imc LIKE 'edad'")
    existe_edad = cursor.fetchone()

    if not existe_edad:
        cursor.execute("""
            ALTER TABLE registros_imc
            ADD COLUMN edad INT NOT NULL DEFAULT 0 AFTER nombre
        """)

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

@app.route('/')
def main():
    return render_template('portada.html')

@app.route("/inicio")
def principal():
    return render_template("inicio.html")

@app.route("/historia")
def historia():
    return render_template("historia.html")

@app.route("/quimica")
def quimica():
    return render_template("quimica.html")


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

    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            edad = int(request.form.get('edad'))
            genero = request.form.get('genero')
            peso = float(request.form.get('peso'))
            altura = float(request.form.get('altura'))

            if nombre == "" or genero == "":
                error = "Debes llenar todos los campos."

            elif edad <= 0 or edad > 120:
                error = "La edad no es válida."

            elif peso <= 0 or peso > 400:
                error = "El peso no es válido."

            elif altura <= 0 or altura > 2.50:
                error = "La altura no es válida. Recuerda escribirla en metros, por ejemplo 1.70."

            else:
                resultado = peso / (altura * altura)
                resultado = round(resultado, 2)

                menor_edad = edad < 18

                if resultado < 18.5:
                    categoria = "Bajo peso"
                    clave_img = "bajo_peso"
                    alimentacion = "Aumentar alimentos nutritivos como huevo, pollo, arroz, avena, frutas, verduras, leche y frutos secos."
                    ejercicios = "Ejercicios ligeros de fuerza, caminatas y actividad física moderada."
                    recomendacion = "Tu IMC indica bajo peso. Lo ideal es mejorar la alimentación poco a poco y no saltarse comidas."

                elif resultado < 25:
                    categoria = "Peso normal o saludable"
                    clave_img = "normal"
                    alimentacion = "Mantener una alimentación balanceada con proteínas, verduras, frutas, agua natural y porciones adecuadas."
                    ejercicios = "Caminar, correr suave, bicicleta, deportes o ejercicios de fuerza 3 a 5 veces por semana."
                    recomendacion = "Tu IMC está en un rango saludable. Vas bien, solo mantén buenos hábitos."

                elif resultado < 30:
                    categoria = "Sobrepeso"
                    clave_img = "sobrepeso"
                    alimentacion = "Reducir refrescos, frituras, pan dulce y comida rápida. Aumentar verduras, agua y comidas caseras."
                    ejercicios = "Caminar 30 minutos, bicicleta, ejercicios de bajo impacto y actividad constante durante la semana."
                    recomendacion = "Tu IMC indica sobrepeso. Se recomienda mejorar hábitos de alimentación y moverse más."

                elif resultado < 35:
                    categoria = "Obesidad grado I"
                    clave_img = "obesidad1"
                    alimentacion = "Evitar exceso de azúcar, refrescos y comida grasosa. Comer más verduras, proteína y tomar agua."
                    ejercicios = "Iniciar con caminatas, bicicleta fija o ejercicios de bajo impacto."
                    recomendacion = "Tu IMC indica obesidad grado I. Lo mejor es empezar con cambios pequeños pero constantes."

                elif resultado < 40:
                    categoria = "Obesidad grado II"
                    clave_img = "obesidad2"
                    alimentacion = "Llevar una alimentación más controlada, reducir porciones grandes y evitar bebidas azucaradas."
                    ejercicios = "Ejercicio de bajo impacto como caminar, nadar o bicicleta, aumentando poco a poco."
                    recomendacion = "Tu IMC indica obesidad grado II. Es recomendable cuidar más la alimentación y buscar orientación profesional."

                else:
                    categoria = "Obesidad grado III u obesidad mórbida"
                    clave_img = "obesidad3"
                    alimentacion = "Se recomienda un plan alimenticio supervisado, evitando dietas extremas y comida ultraprocesada."
                    ejercicios = "Actividad física suave y segura, como caminatas cortas, siempre aumentando poco a poco."
                    recomendacion = "Tu IMC indica obesidad grado III. Es importante consultar a un profesional de salud."

                beneficios = "Llevar una vida saludable ayuda a tener más energía, dormir mejor, mejorar la condición física y prevenir enfermedades."

                if menor_edad:
                    imagen_figura = "img/menor.png"
                else:
                    imagen_figura = "img/" + clave_img + "_" + genero + ".png"

                porcentaje_grafica = round((resultado / 45) * 100, 2)

                if porcentaje_grafica > 100:
                    porcentaje_grafica = 100

                cursor.execute("""
                    INSERT INTO registros_imc (nombre, edad, genero, peso, altura, imc, categoria)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, edad, genero, peso, altura, resultado, categoria))

                conexion.commit()

        except ValueError:
            error = "Revisa los datos. Peso, altura y edad deben ser números."

    cursor.execute("SELECT * FROM registros_imc ORDER BY id DESC")
    registros = cursor.fetchall()

    cursor.close()
    conexion.close()

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


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        peso = float(request.form.get('peso'))
        altura = float(request.form.get('altura'))

        imc = peso / (altura * altura)
        imc = round(imc, 2)

        if imc < 18.5:
            categoria = "Bajo peso"
        elif imc < 25:
            categoria = "Peso normal"
        elif imc < 30:
            categoria = "Sobrepeso"
        else:
            categoria = "Obesidad"

        cursor.execute("""
            UPDATE registros_imc
            SET nombre=%s, peso=%s, altura=%s, imc=%s, categoria=%s
            WHERE id=%s
        """, (nombre, peso, altura, imc, categoria, id))

        conexion.commit()

        cursor.close()
        conexion.close()

        return redirect(url_for('imc'))

    cursor.execute("SELECT * FROM registros_imc WHERE id=%s", (id,))
    registro = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template('editar_imc.html', registro=registro)


@app.route('/borrar/<int:id>')
def borrar(id):
    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM registros_imc WHERE id=%s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    return redirect(url_for('imc'))


if __name__ == "__main__":
    crear_base_datos()
    app.run(debug=True)