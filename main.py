from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_my_secret_keysy'


def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="salud"
    )

@app.route('/')
def main():
    return render_template('inicio.html')


@app.route('/imc', methods=['GET', 'POST'])
def imc():
    resultado = None
    categoria = None
    nombre = None

    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        peso = float(request.form.get('peso'))
        altura = float(request.form.get('altura'))

        resultado = peso / (altura * altura)
        resultado = round(resultado, 2)

        if resultado < 18.5:
            categoria = "Bajo peso"
        elif resultado < 25:
            categoria = "Peso normal"
        elif resultado < 30:
            categoria = "Sobrepeso"
        else:
            categoria = "Obesidad"

        cursor.execute("""
            INSERT INTO registros_imc (nombre, peso, altura, imc, categoria)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, peso, altura, resultado, categoria))

        conexion.commit()

    cursor.execute("SELECT * FROM registros_imc ORDER BY id DESC")
    registros = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        'imc.html',
        nombre=nombre,
        resultado=resultado,
        categoria=categoria,
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
    app.run(debug=True)