from flask import Flask, render_template, request, redirect, url_for, session, flash
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from types import SimpleNamespace

try:
    import pyodbc
except Exception:
    pyodbc = None


app = Flask(__name__)
app.secret_key = 'clave_secreta_minimarket_damir_2026'

app.config['UPLOAD_FOLDER_PRODUCTOS'] = str(Path(app.root_path) / 'static' / 'img' / 'productos')
app.config['UPLOAD_FOLDER_CLIENTES'] = str(Path(app.root_path) / 'static' / 'img' / 'clientes')

EXTENSIONES_IMAGEN = {'png', 'jpg', 'jpeg', 'webp', 'gif', 'svg'}


def es_imagen_valida(nombre_archivo):
    return '.' in nombre_archivo and nombre_archivo.rsplit('.', 1)[1].lower() in EXTENSIONES_IMAGEN


def guardar_imagen_subida(archivo, carpeta_config, subcarpeta):
    if not archivo or not archivo.filename:
        return None

    if not es_imagen_valida(archivo.filename):
        return None

    carpeta = Path(app.config[carpeta_config])
    carpeta.mkdir(parents=True, exist_ok=True)

    nombre_base = secure_filename(archivo.filename)
    nombre_final = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{nombre_base}"
    ruta_final = carpeta / nombre_final
    archivo.save(ruta_final)

    return f"img/{subcarpeta}/{nombre_final}"


def capitalizar_datos(texto):
    if texto is None:
        return None
    return ' '.join(palabra.capitalize() for palabra in str(texto).strip().split())


def titulo(texto):
    return ' '.join(palabra.capitalize() for palabra in str(texto).split())


def fila_demo(**kwargs):
    return SimpleNamespace(**kwargs)


def obtener_conexion():
    """
    Localmente usa SQL Server Management Studio.
    En Render, si pyodbc o SQL Server no están disponibles, lanza excepción.
    Las rutas tienen modo demo para no romper la página online.
    """
    if pyodbc is None:
        raise Exception("SQL Server no disponible en Render")

    conexion = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=PC_HALION;'
        'DATABASE=Minimarkt_Damir;'
        'Trusted_Connection=yes;'
    )
    return conexion


def asegurar_columnas_extra(cursor):
    cursor.execute("""
        IF COL_LENGTH('Clientes', 'Foto') IS NULL
        BEGIN
            ALTER TABLE Clientes ADD Foto VARCHAR(250) NULL
        END
    """)


def crear_bloc_notas(tipo, datos):
    carpeta_txt = Path('registros_txt')
    carpeta_txt.mkdir(exist_ok=True)

    fecha_archivo = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_seguro = str(datos.get('Nombre', 'Registro')).replace(' ', '_')
    archivo = carpeta_txt / f"{tipo}_{nombre_seguro}_{fecha_archivo}.txt"

    with open(archivo, 'w', encoding='utf-8') as bloc:
        bloc.write(f"MINIMARKET DAMIR - {tipo.upper()} REGISTRADO\n")
        bloc.write('=' * 45 + '\n')
        bloc.write(f"Fecha de creación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        for campo, valor in datos.items():
            bloc.write(f"{campo}: {valor}\n")

        bloc.write('\nEste archivo se creó automáticamente al guardar el registro.\n')

    return archivo


CLIENTES_DEMO = [
    ('Ana', 'Quispe', 'Av. Arequipa 1250, Lima'),
    ('Luis', 'Flores', 'Jr. Cusco 455, Lima'),
    ('Maria', 'Huaman', 'Av. Grau 230, Barranco'),
    ('Carlos', 'Ramos', 'Calle Los Pinos 88, Surco'),
    ('Rosa', 'Mamani', 'Av. La Marina 710, San Miguel'),
    ('Jorge', 'Torres', 'Jr. Amazonas 321, Cercado'),
    ('Lucia', 'Vargas', 'Av. Benavides 1420, Miraflores'),
    ('Diego', 'Castro', 'Calle Lima 987, Ate'),
    ('Valeria', 'Paredes', 'Av. Universitaria 650, Los Olivos'),
    ('Miguel', 'Salazar', 'Jr. Junin 541, Callao')
]

PRODUCTOS_DEMO = [
    ('Arroz Extra', 'Costeño', 4.80, 'Abarrotes', 'arroz.svg'),
    ('Aceite Vegetal', 'Primor', 9.90, 'Abarrotes', 'aceite.svg'),
    ('Fideos Tallarin', 'Don Vittorio', 4.20, 'Abarrotes', 'fideos.svg'),
    ('Azucar Rubia', 'Cartavio', 4.50, 'Abarrotes', 'azucar.svg'),
    ('Atun En Trozos', 'Florida', 6.70, 'Abarrotes', 'atun.svg'),
    ('Quinua Seleccionada', 'Valle Andino', 8.90, 'Abarrotes', 'quinua.svg'),
    ('Lenteja Bebé', 'Costeño', 6.10, 'Abarrotes', 'lenteja.svg'),
    ('Harina Preparada', 'Blanca Flor', 5.70, 'Abarrotes', 'harina.svg'),

    ('Leche Evaporada', 'Gloria', 4.30, 'Desayuno', 'leche.svg'),
    ('Avena Tradicional', 'Quaker', 5.80, 'Desayuno', 'avena.svg'),
    ('Cafe Instantaneo', 'Altomayo', 12.50, 'Desayuno', 'cafe.svg'),
    ('Pan Molde', 'Bimbo', 8.90, 'Desayuno', 'pan.svg'),
    ('Mermelada Fresa', 'Fanny', 7.20, 'Desayuno', 'mermelada.svg'),
    ('Cereal Chocolate', 'Angel', 10.50, 'Desayuno', 'cereal.svg'),
    ('Mantequilla Barra', 'Laive', 7.40, 'Desayuno', 'mantequilla.svg'),

    ('Agua Sin Gas', 'San Luis', 2.00, 'Bebidas', 'agua.svg'),
    ('Gaseosa Inca Kola', 'Inca Kola', 3.80, 'Bebidas', 'gaseosa.svg'),
    ('Jugo Durazno', 'Frugos', 4.50, 'Bebidas', 'jugo.svg'),
    ('Bebida Rehidratante', 'Sporade', 3.20, 'Bebidas', 'sporade.svg'),
    ('Chicha Morada', 'Gloria', 4.90, 'Bebidas', 'chicha.svg'),
    ('Energizante Lata', 'Volt', 3.50, 'Bebidas', 'volt.svg'),

    ('Papas Onduladas', 'Lays', 3.50, 'Snacks', 'papas.svg'),
    ('Galleta Chocolate', 'Casino', 2.20, 'Snacks', 'galleta.svg'),
    ('Chocolate Sublime', 'Nestle', 2.50, 'Snacks', 'chocolate.svg'),
    ('Cereal Barrita', 'Angel', 1.80, 'Snacks', 'barrita.svg'),
    ('Chifles Norteños', 'Tondero', 4.90, 'Snacks', 'chifles.svg'),
    ('Maní Salado', 'Karinto', 2.60, 'Snacks', 'mani.svg'),
    ('Cuates Picante', 'Karinto', 1.40, 'Snacks', 'cuates.svg'),

    ('Detergente Bolsa', 'Bolivar', 8.50, 'Limpieza', 'detergente.svg'),
    ('Lavavajilla Limon', 'Sapolio', 4.00, 'Limpieza', 'lavavajilla.svg'),
    ('Lejia Tradicional', 'Clorox', 3.60, 'Limpieza', 'lejia.svg'),
    ('Papel Higienico', 'Elite', 10.90, 'Limpieza', 'papel.svg'),
    ('Limpiatodo Floral', 'Poett', 5.90, 'Limpieza', 'limpiatodo.svg'),
    ('Suavizante Azul', 'Bolivar', 9.30, 'Limpieza', 'suavizante.svg'),

    ('Yogurt Fresa', 'Gloria', 5.60, 'Lácteos', 'yogurt.svg'),
    ('Queso Fresco', 'Laive', 11.90, 'Lácteos', 'queso.svg'),
    ('Manjar Blanco', 'Nestle', 8.20, 'Lácteos', 'manjar.svg'),

    ('Jabon Tocador', 'Aval', 2.80, 'Cuidado Personal', 'jabon.svg'),
    ('Shampoo Savila', 'Sedal', 12.90, 'Cuidado Personal', 'shampoo.svg'),
    ('Pasta Dental', 'Dento', 5.50, 'Cuidado Personal', 'pasta_dental.svg'),
    ('Cepillo Dental', 'Colgate', 4.20, 'Cuidado Personal', 'cepillo.svg'),
    ('Pañitos Húmedos', 'Huggies', 7.80, 'Cuidado Personal', 'panitos.svg'),

    ('Filete De Atún', 'Florida', 7.30, 'Conservas', 'filete_atun.svg'),
    ('Sardina En Salsa', 'A-1', 5.40, 'Conservas', 'sardina.svg'),
    ('Durazno En Almibar', 'Aconcagua', 9.70, 'Conservas', 'durazno.svg'),
    ('Frejol En Lata', 'Hoja Redonda', 6.20, 'Conservas', 'frejol_lata.svg'),

    ('Pollo Entero', 'San Fernando', 18.90, 'Carnes', 'pollo.svg'),
    ('Hamburguesa Pack', 'Otto Kunz', 14.50, 'Carnes', 'hamburguesa.svg'),
    ('Hot Dog Clásico', 'San Fernando', 9.80, 'Carnes', 'hotdog.svg'),
    ('Chorizo Parrillero', 'Braedt', 13.90, 'Carnes', 'chorizo.svg'),

    ('Manzana Delicia', 'Perú', 3.90, 'Frutas Y Verduras', 'manzana.svg'),
    ('Plátano Seda', 'Perú', 2.80, 'Frutas Y Verduras', 'platano.svg'),
    ('Papa Blanca', 'Perú', 2.40, 'Frutas Y Verduras', 'papa_blanca.svg'),
    ('Cebolla Roja', 'Perú', 2.70, 'Frutas Y Verduras', 'cebolla.svg')
]


def crear_imagenes_producto_demo():
    carpeta = Path(app.root_path) / 'static' / 'img' / 'productos'
    carpeta.mkdir(parents=True, exist_ok=True)

    for nombre, marca, precio, pasillo, imagen in PRODUCTOS_DEMO:
        archivo = carpeta / imagen

        if archivo.exists():
            continue

        etiqueta = nombre.split()[0]
        svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='500' height='500' viewBox='0 0 500 500'>
<rect width='500' height='500' rx='48' fill='#f7fbef'/>
<circle cx='250' cy='205' r='120' fill='#a7d800' opacity='0.9'/>
<rect x='130' y='170' width='240' height='190' rx='28' fill='#ffffff' stroke='#334155' stroke-width='8'/>
<text x='250' y='242' font-family='Arial' font-size='44' font-weight='700' text-anchor='middle' fill='#334155'>{etiqueta}</text>
<text x='250' y='300' font-family='Arial' font-size='30' font-weight='700' text-anchor='middle' fill='#6b8e00'>{marca}</text>
<text x='250' y='395' font-family='Arial' font-size='28' font-weight='700' text-anchor='middle' fill='#334155'>S/ {precio:.2f}</text>
</svg>"""
        archivo.write_text(svg, encoding='utf-8')


def productos_demo_filtrados(nombre_pasillo=None):
    crear_imagenes_producto_demo()

    productos = []
    for i, (nombre, marca, precio, pasillo, imagen) in enumerate(PRODUCTOS_DEMO, start=1):
        if nombre_pasillo and pasillo != nombre_pasillo:
            continue

        productos.append(fila_demo(
            IdProducto=i,
            Nombre=titulo(nombre),
            Marca=titulo(marca),
            Precio=float(precio),
            Pasillo=pasillo,
            Imagen=f'img/productos/{imagen}'
        ))

    return productos


def clientes_demo_lista():
    clientes = []

    for i in range(1, 51):
        nombre, apellido, direccion = CLIENTES_DEMO[(i - 1) % len(CLIENTES_DEMO)]

        clientes.append(fila_demo(
            IdCliente=i,
            Nombre=titulo(nombre),
            Apellido=titulo(apellido),
            Celular='9' + str(10000000 + i * 13579)[-8:],
            Correo=f'{nombre.lower()}.{apellido.lower()}.{i}@demo.com',
            Direccion=titulo(direccion),
            Foto=None,
            Letra=titulo(nombre)[0],
            Total=5,
            Contraseña=generate_password_hash('123456')
        ))

    return clientes


def sembrar_datos_demo():
    crear_imagenes_producto_demo()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute('SELECT COUNT(*) FROM Clientes')
    total_clientes = cursor.fetchone()[0]

    clave_hash = generate_password_hash('123456')

    if total_clientes < 50:
        for i in range(50 - total_clientes):
            nombre, apellido, direccion = CLIENTES_DEMO[i % len(CLIENTES_DEMO)]
            correo_demo = f"{nombre.lower()}.{apellido.lower()}.{i + 1}@demo.com"
            celular_demo = '9' + str(10000000 + i * 13579)[-8:]

            cursor.execute('SELECT 1 FROM Clientes WHERE Correo = ?', correo_demo)

            if not cursor.fetchone():
                cursor.execute(
                    'INSERT INTO Clientes (Nombre, Apellido, Celular, Correo, Direccion, Contraseña) VALUES (?, ?, ?, ?, ?, ?)',
                    titulo(nombre), titulo(apellido), celular_demo, correo_demo, titulo(direccion), clave_hash
                )

    cursor.execute('SELECT COUNT(*) FROM Productos')
    total_productos = cursor.fetchone()[0]

    if total_productos < 50:
        for i in range(50 - total_productos):
            nombre, marca, precio, pasillo, imagen = PRODUCTOS_DEMO[i % len(PRODUCTOS_DEMO)]
            nombre_demo = titulo(nombre if i < len(PRODUCTOS_DEMO) else f'{nombre} Familiar')
            precio_demo = round(float(precio) + (i % 7) * 0.35, 2)

            cursor.execute(
                'INSERT INTO Productos (Nombre, Marca, Precio, Pasillo, Imagen) VALUES (?, ?, ?, ?, ?)',
                nombre_demo, titulo(marca), precio_demo, pasillo, f'img/productos/{imagen}'
            )

    conexion.commit()
    conexion.close()


@app.route('/')
def index():
    try:
        sembrar_datos_demo()
    except Exception:
        crear_imagenes_producto_demo()

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT DISTINCT Pasillo FROM Productos WHERE Pasillo IS NOT NULL AND Pasillo <> '' ORDER BY Pasillo")
        pasillos = [fila[0] for fila in cursor.fetchall()]
        conexion.close()
    except Exception:
        pasillos = ['Abarrotes', 'Bebidas', 'Desayuno', 'Snacks', 'Limpieza', 'Lácteos', 'Cuidado Personal', 'Conservas', 'Carnes', 'Frutas Y Verduras']

    return render_template('index.html', pasillos=pasillos)


def productos_por_pasillo(nombre_pasillo):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT IdProducto, Nombre, Marca, Precio, Pasillo, Imagen
            FROM Productos
            WHERE Pasillo = ?
            ORDER BY IdProducto DESC
        """, nombre_pasillo)

        productos = cursor.fetchall()
        conexion.close()

        return productos

    except Exception:
        return productos_demo_filtrados(nombre_pasillo)


def renderizar_pasillo(nombre_pasillo, icono, subtitulo):
    productos = productos_por_pasillo(nombre_pasillo)
    return render_template('pasillo.html', productos=productos, pasillo=nombre_pasillo, icono=icono, subtitulo=subtitulo)


@app.route('/abarrotes')
def abarrotes():
    return renderizar_pasillo('Abarrotes', 'fa-mortar-pestle', 'Arroz, Aceite, Fideos, Menestras Y Más Productos Peruanos.')


@app.route('/bebidas')
def bebidas():
    return renderizar_pasillo('Bebidas', 'fa-wine-glass', 'Gaseosas, Aguas, Jugos Y Bebidas Refrescantes.')


@app.route('/desayuno')
def desayuno():
    return renderizar_pasillo('Desayuno', 'fa-egg', 'Leche, Café, Cereales Y Todo Para Iniciar El Día.')


@app.route('/snacks')
def snacks():
    return renderizar_pasillo('Snacks', 'fa-cookie', 'Galletas, Papitas, Chocolates Y Antojos.')


@app.route('/limpieza')
def limpieza():
    return renderizar_pasillo('Limpieza', 'fa-soap', 'Detergentes, Desinfectantes Y Cuidado Del Hogar.')


@app.route('/pasillo/<nombre_pasillo>')
def pasillo_dinamico(nombre_pasillo):
    mapa_pasillos = {
        'abarrotes': 'Abarrotes',
        'bebidas': 'Bebidas',
        'desayuno': 'Desayuno',
        'snacks': 'Snacks',
        'limpieza': 'Limpieza',
        'lacteos': 'Lácteos',
        'cuidado-personal': 'Cuidado Personal',
        'conservas': 'Conservas',
        'carnes': 'Carnes',
        'frutas-y-verduras': 'Frutas Y Verduras'
    }

    nombre_formateado = mapa_pasillos.get(nombre_pasillo, nombre_pasillo.replace('-', ' ').title())
    return renderizar_pasillo(nombre_formateado, 'fa-shop', f'Productos Del Pasillo {nombre_formateado}.')


@app.route('/carrito')
def carrito():
    return render_template('carrito.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM Clientes WHERE Correo = ?", correo)
            usuario = cursor.fetchone()
            conexion.close()

            if usuario and check_password_hash(usuario.Contraseña, contraseña):
                session['usuario_correo'] = usuario.Correo
                session['usuario_nombre'] = usuario.Nombre
                return redirect(url_for('index'))

        except Exception:
            for usuario in clientes_demo_lista():
                if usuario.Correo == correo and check_password_hash(usuario.Contraseña, contraseña):
                    session['usuario_correo'] = usuario.Correo
                    session['usuario_nombre'] = usuario.Nombre
                    return redirect(url_for('index'))

            if correo and contraseña:
                session['usuario_correo'] = correo
                session['usuario_nombre'] = correo.split('@')[0].capitalize()
                return redirect(url_for('index'))

        flash('Correo o contraseña incorrectos.')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = capitalizar_datos(request.form.get('nombre'))
        apellido = capitalizar_datos(request.form.get('apellido'))
        celular = request.form.get('celular')
        correo = request.form.get('correo')
        direccion = capitalizar_datos(request.form.get('direccion'))
        contraseña = request.form.get('contraseña')
        confirmar_contraseña = request.form.get('confirmar_contraseña')

        if contraseña != confirmar_contraseña:
            flash('Las contraseñas no coinciden')
            return redirect(url_for('registro'))

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()

            cursor.execute("SELECT * FROM Clientes WHERE Correo = ?", correo)
            usuario = cursor.fetchone()

            if usuario:
                flash('Este correo ya existe.')
                conexion.close()
                return redirect(url_for('registro'))

            contraseña_hash = generate_password_hash(contraseña)

            cursor.execute("""
                INSERT INTO Clientes
                (Nombre, Apellido, Celular, Correo, Direccion, Contraseña)
                OUTPUT INSERTED.IdCliente
                VALUES (?, ?, ?, ?, ?, ?)
            """, nombre, apellido, celular, correo, direccion, contraseña_hash)

            id_cliente_nuevo = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()

            crear_bloc_notas('cliente', {
                'ID': id_cliente_nuevo,
                'Nombre': nombre,
                'Apellido': apellido,
                'Celular': celular or 'Sin celular',
                'Correo': correo,
                'Dirección': direccion or 'Sin dirección'
            })

        except Exception:
            crear_bloc_notas('cliente_demo', {
                'Nombre': nombre,
                'Apellido': apellido,
                'Celular': celular or 'Sin celular',
                'Correo': correo,
                'Dirección': direccion or 'Sin dirección'
            })
            flash('Registro creado en modo demostración.')

        session['usuario_nombre'] = nombre
        session['usuario_correo'] = correo

        return redirect(url_for('perfil'))

    return render_template('registro.html')


@app.route('/perfil')
def perfil():
    if 'usuario_correo' not in session:
        return redirect(url_for('login'))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("SELECT * FROM Clientes WHERE Correo = ?", session['usuario_correo'])
        usuario = cursor.fetchone()

        conexion.close()

    except Exception:
        usuario = fila_demo(
            Nombre=session.get('usuario_nombre', 'Usuario'),
            Apellido='',
            Celular='',
            Correo=session.get('usuario_correo', ''),
            Direccion='',
            Foto=None
        )

    return render_template('perfil.html', usuario=usuario, correo=session['usuario_correo'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        clave = request.form.get('clave_admin')

        if clave == "admin":
            session['admin'] = True
            return redirect(url_for('index'))

        flash('Contraseña incorrecta.')

    return render_template('admin_login.html')


@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    return render_template('admin_dashboard.html')


@app.route('/admin/sembrar-datos')
def admin_sembrar_datos():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        sembrar_datos_demo()
        flash('Se crearon datos ficticios en SQL Server.')
    except Exception:
        flash('Render está en modo demostración. Los datos demo ya están disponibles.')

    return redirect(request.referrer or url_for('admin_dashboard'))


@app.route('/admin/clientes', methods=['GET', 'POST'])
def admin_clientes():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        asegurar_columnas_extra(cursor)
        conexion.commit()

        if request.method == 'POST':
            nombre = capitalizar_datos(request.form.get('nombre'))
            apellido = capitalizar_datos(request.form.get('apellido'))
            celular = request.form.get('celular')
            correo = request.form.get('correo')
            direccion = capitalizar_datos(request.form.get('direccion'))
            contraseña = request.form.get('contraseña')
            foto = guardar_imagen_subida(request.files.get('foto'), 'UPLOAD_FOLDER_CLIENTES', 'clientes')

            if not nombre or not apellido or not correo or not contraseña:
                flash('Completa nombre, apellido, correo y contraseña.')
                conexion.close()
                return redirect(url_for('admin_clientes'))

            cursor.execute("SELECT * FROM Clientes WHERE Correo = ?", correo)
            cliente_existente = cursor.fetchone()

            if cliente_existente:
                flash('Ese correo ya está registrado.')
                conexion.close()
                return redirect(url_for('admin_clientes'))

            contraseña_hash = generate_password_hash(contraseña)

            cursor.execute("""
                INSERT INTO Clientes
                (Nombre, Apellido, Celular, Correo, Direccion, Contraseña, Foto)
                OUTPUT INSERTED.IdCliente
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, nombre, apellido, celular, correo, direccion, contraseña_hash, foto)

            id_cliente_nuevo = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()

            crear_bloc_notas('cliente', {
                'ID': id_cliente_nuevo,
                'Nombre': nombre,
                'Apellido': apellido,
                'Celular': celular or 'Sin celular',
                'Correo': correo,
                'Dirección': direccion or 'Sin dirección',
                'Foto': foto or 'Sin foto'
            })

            flash('Cliente agregado correctamente.')
            return redirect(url_for('admin_clientes'))

        cursor.execute("""
            SELECT IdCliente, Nombre, Apellido, Celular, Correo, Direccion, Foto
            FROM Clientes
            ORDER BY IdCliente DESC
        """)
        clientes = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM Clientes")
        total_clientes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Clientes WHERE Celular IS NOT NULL AND Celular <> ''")
        clientes_con_celular = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Clientes WHERE Direccion IS NOT NULL AND Direccion <> ''")
        clientes_con_direccion = cursor.fetchone()[0]

        cursor.execute("SELECT TOP 5 IdCliente, Nombre, Apellido, Correo FROM Clientes ORDER BY IdCliente DESC")
        ultimos_clientes = cursor.fetchall()

        cursor.execute("""
            SELECT TOP 6 LEFT(Nombre, 1) AS Letra, COUNT(*) AS Total
            FROM Clientes
            GROUP BY LEFT(Nombre, 1)
            ORDER BY Total DESC
        """)
        clientes_por_inicial = cursor.fetchall()

        conexion.close()

    except Exception:
        if request.method == 'POST':
            flash('Modo demo Render: el cliente no se guardó en SQL, pero la página funciona para presentación.')
            return redirect(url_for('admin_clientes'))

        clientes = clientes_demo_lista()
        total_clientes = len(clientes)
        clientes_con_celular = len([c for c in clientes if c.Celular])
        clientes_con_direccion = len([c for c in clientes if c.Direccion])
        ultimos_clientes = clientes[:5]

        conteo = {}
        for c in clientes:
            conteo[c.Nombre[0]] = conteo.get(c.Nombre[0], 0) + 1

        clientes_por_inicial = [
            fila_demo(Letra=k, Total=v)
            for k, v in sorted(conteo.items())[:6]
        ]

    clientes_sin_celular = total_clientes - clientes_con_celular
    clientes_sin_direccion = total_clientes - clientes_con_direccion

    return render_template(
        'admin_clientes.html',
        clientes=clientes,
        total_clientes=total_clientes,
        clientes_con_celular=clientes_con_celular,
        clientes_con_direccion=clientes_con_direccion,
        clientes_sin_celular=clientes_sin_celular,
        clientes_sin_direccion=clientes_sin_direccion,
        clientes_por_inicial=clientes_por_inicial,
        ultimos_clientes=ultimos_clientes
    )


@app.route('/admin/productos', methods=['GET', 'POST'])
def admin_productos():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        asegurar_columnas_extra(cursor)
        conexion.commit()

        if request.method == 'POST':
            nombre = capitalizar_datos(request.form.get('nombre'))
            marca = capitalizar_datos(request.form.get('marca'))
            precio = request.form.get('precio')
            pasillo = capitalizar_datos(request.form.get('pasillo'))
            imagen = request.form.get('imagen')
            imagen_subida = guardar_imagen_subida(request.files.get('imagen_archivo'), 'UPLOAD_FOLDER_PRODUCTOS', 'productos')

            if imagen_subida:
                imagen = imagen_subida

            if not nombre or not marca or not precio or not pasillo or not imagen:
                flash('Completa todos los datos del producto.')
                conexion.close()
                return redirect(url_for('admin_productos'))

            cursor.execute("""
                INSERT INTO Productos
                (Nombre, Marca, Precio, Pasillo, Imagen)
                OUTPUT INSERTED.IdProducto
                VALUES (?, ?, ?, ?, ?)
            """, nombre, marca, precio, pasillo, imagen)

            id_producto_nuevo = cursor.fetchone()[0]
            conexion.commit()
            conexion.close()

            crear_bloc_notas('producto', {
                'ID': id_producto_nuevo,
                'Nombre': nombre,
                'Marca': marca,
                'Precio': precio,
                'Pasillo': pasillo,
                'Imagen': imagen
            })

            flash('Producto agregado correctamente.')
            return redirect(url_for('admin_productos'))

        cursor.execute("""
            SELECT IdProducto, Nombre, Marca, Precio, Pasillo, Imagen
            FROM Productos
            ORDER BY IdProducto DESC
        """)
        productos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM Productos")
        total_productos = cursor.fetchone()[0]

        cursor.execute("SELECT ISNULL(AVG(CAST(Precio AS FLOAT)), 0) FROM Productos")
        precio_promedio = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT Pasillo) FROM Productos")
        total_pasillos = cursor.fetchone()[0]

        cursor.execute("SELECT TOP 1 Nombre, Marca, Precio FROM Productos ORDER BY Precio DESC")
        producto_mayor_precio = cursor.fetchone()

        cursor.execute("SELECT Pasillo, COUNT(*) AS Total FROM Productos GROUP BY Pasillo ORDER BY Total DESC")
        productos_por_pasillo = cursor.fetchall()

        cursor.execute("SELECT TOP 5 Nombre, Marca, Precio, Imagen FROM Productos ORDER BY IdProducto DESC")
        ultimos_productos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) FROM Productos WHERE Precio <= 5")
        productos_economicos = cursor.fetchone()[0]

        conexion.close()

    except Exception:
        if request.method == 'POST':
            flash('Modo demo Render: el producto no se guardó en SQL, pero la página funciona para presentación.')
            return redirect(url_for('admin_productos'))

        productos = productos_demo_filtrados()
        total_productos = len(productos)
        precio_promedio = sum(p.Precio for p in productos) / max(total_productos, 1)
        total_pasillos = len(set(p.Pasillo for p in productos))
        producto_mayor_precio = max(productos, key=lambda p: p.Precio) if productos else None

        conteo = {}
        for p in productos:
            conteo[p.Pasillo] = conteo.get(p.Pasillo, 0) + 1

        productos_por_pasillo = [
            fila_demo(Pasillo=k, Total=v)
            for k, v in sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        ]

        ultimos_productos = productos[:5]
        productos_economicos = len([p for p in productos if p.Precio <= 5])

    return render_template(
        'admin_productos.html',
        productos=productos,
        total_productos=total_productos,
        precio_promedio=precio_promedio,
        total_pasillos=total_pasillos,
        producto_mayor_precio=producto_mayor_precio,
        productos_por_pasillo=productos_por_pasillo,
        ultimos_productos=ultimos_productos,
        productos_economicos=productos_economicos
    )


@app.route('/admin/clientes/editar/<int:id_cliente>', methods=['POST'])
def admin_editar_cliente(id_cliente):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        nombre = capitalizar_datos(request.form.get('nombre'))
        apellido = capitalizar_datos(request.form.get('apellido'))
        celular = request.form.get('celular')
        correo = request.form.get('correo')
        direccion = capitalizar_datos(request.form.get('direccion'))
        contraseña = request.form.get('contraseña')
        foto = guardar_imagen_subida(request.files.get('foto'), 'UPLOAD_FOLDER_CLIENTES', 'clientes')

        if not nombre or not apellido or not correo:
            flash('Completa nombre, apellido y correo para editar el cliente.')
            return redirect(url_for('admin_clientes'))

        conexion = obtener_conexion()
        cursor = conexion.cursor()
        asegurar_columnas_extra(cursor)
        conexion.commit()

        cursor.execute("SELECT * FROM Clientes WHERE Correo = ? AND IdCliente <> ?", correo, id_cliente)
        cliente_existente = cursor.fetchone()

        if cliente_existente:
            flash('No se pudo editar: ese correo ya pertenece a otro cliente.')
            conexion.close()
            return redirect(url_for('admin_clientes'))

        campos = ['Nombre = ?', 'Apellido = ?', 'Celular = ?', 'Correo = ?', 'Direccion = ?']
        valores = [nombre, apellido, celular, correo, direccion]

        if contraseña:
            campos.append('Contraseña = ?')
            valores.append(generate_password_hash(contraseña))

        if foto:
            campos.append('Foto = ?')
            valores.append(foto)

        valores.append(id_cliente)

        cursor.execute(f"UPDATE Clientes SET {', '.join(campos)} WHERE IdCliente = ?", valores)
        conexion.commit()
        conexion.close()

        flash('Cliente editado correctamente.')

    except Exception:
        flash('Modo demo Render: edición simulada.')

    return redirect(url_for('admin_clientes'))


@app.route('/admin/clientes/eliminar/<int:id_cliente>', methods=['POST'])
def admin_eliminar_cliente(id_cliente):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM Clientes WHERE IdCliente = ?", id_cliente)

        conexion.commit()
        conexion.close()

        flash('Cliente eliminado correctamente.')

    except Exception:
        flash('Modo demo Render: eliminación simulada.')

    return redirect(url_for('admin_clientes'))


@app.route('/admin/productos/editar/<int:id_producto>', methods=['POST'])
def admin_editar_producto(id_producto):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        nombre = capitalizar_datos(request.form.get('nombre'))
        marca = capitalizar_datos(request.form.get('marca'))
        precio = request.form.get('precio')
        pasillo = capitalizar_datos(request.form.get('pasillo'))
        imagen = request.form.get('imagen')
        imagen_subida = guardar_imagen_subida(request.files.get('imagen_archivo'), 'UPLOAD_FOLDER_PRODUCTOS', 'productos')

        if imagen_subida:
            imagen = imagen_subida

        if not nombre or not marca or not precio or not pasillo or not imagen:
            flash('Completa todos los datos para editar el producto.')
            return redirect(url_for('admin_productos'))

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE Productos
            SET Nombre = ?, Marca = ?, Precio = ?, Pasillo = ?, Imagen = ?
            WHERE IdProducto = ?
        """, nombre, marca, precio, pasillo, imagen, id_producto)

        conexion.commit()
        conexion.close()

        flash('Producto editado correctamente.')

    except Exception:
        flash('Modo demo Render: edición simulada.')

    return redirect(url_for('admin_productos'))


@app.route('/admin/productos/eliminar/<int:id_producto>', methods=['POST'])
def admin_eliminar_producto(id_producto):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM Productos WHERE IdProducto = ?", id_producto)

        conexion.commit()
        conexion.close()

        flash('Producto eliminado correctamente.')

    except Exception:
        flash('Modo demo Render: eliminación simulada.')

    return redirect(url_for('admin_productos'))


if __name__ == '__main__':
    app.run(debug=True)
