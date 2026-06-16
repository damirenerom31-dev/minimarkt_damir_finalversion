document.addEventListener('DOMContentLoaded', () => {
    // Inicializar el carrito desde localStorage de forma segura
    function leerCarritoSeguro() {
        try {
            const datos = JSON.parse(localStorage.getItem('carrito-tienda')) || [];
            if (!Array.isArray(datos)) return [];
            return datos
                .filter(item => item && item.nombre && !isNaN(parseFloat(item.precio)))
                .map(item => ({
                    nombre: String(item.nombre),
                    precio: parseFloat(item.precio),
                    imagen: item.imagen || '',
                    cantidad: Math.max(1, parseInt(item.cantidad || 1))
                }));
        } catch (error) {
            localStorage.removeItem('carrito-tienda');
            return [];
        }
    }

    let carrito = leerCarritoSeguro();
    
    actualizarBadgeCarrito();

    if (document.getElementById('lista-productos-carrito')) {
        renderizarCarrito();
    }

    const btnVaciarCarrito = document.getElementById('btn-vaciar-carrito');
    if (btnVaciarCarrito) {
        btnVaciarCarrito.addEventListener('click', () => {
            carrito = [];
            localStorage.removeItem('carrito-tienda');
            localStorage.removeItem('carrito');
            localStorage.removeItem('productos-carrito');
            guardarYActualizar();
            renderizarCarrito();
            alert('El Carrito Fue Vaciado Correctamente.');
        });
    }

    /* ==========================================================================
       CAPTURAR BOTONES "AGREGAR" EN LOS PASILLOS
       ========================================================================== */
    const botonesAgregar = document.querySelectorAll('.btn-agregar');
    botonesAgregar.forEach((boton) => {
        boton.addEventListener('click', (e) => {
            e.stopPropagation(); 
            
            const tarjeta = boton.closest('.tarjeta-producto');
            let nombre = "";
            let precio = 0;
            let imagenSrc = "";

            // Caso A: Atributos HTML data-* (Como en bebidas.html)
            if (boton.hasAttribute('data-nombre') && boton.hasAttribute('data-precio')) {
                nombre = boton.getAttribute('data-nombre').trim();
                precio = parseFloat(boton.getAttribute('data-precio'));
            } 
            // Caso B: Leer del texto de la tarjeta (Como en abarrotes, desayunos, etc.)
            else if (tarjeta) {
                const elementoNombre = tarjeta.querySelector('.nombre');
                const elementoPrecio = tarjeta.querySelector('.precio-actual');
                
                if (elementoNombre) nombre = elementoNombre.innerText.trim();
                if (elementoPrecio) {
                    // Extrae únicamente los números y el punto decimal del texto del precio
                    let texto = elementoPrecio.innerText;
                    let soloNumeros = texto.replace(/[^0-9.]/g, ''); 
                    precio = parseFloat(soloNumeros);
                }
            }

            // Capturar imagen
            if (tarjeta) {
                const imgElemento = tarjeta.querySelector('.producto-imagen img');
                if (imgElemento) imagenSrc = imgElemento.src;
            }

            if (nombre && !isNaN(precio) && precio > 0) {
                agregarAlCarrito(nombre, precio, imagenSrc);
            }
        });
    });

    function agregarAlCarrito(nombre, precio, imagen) {
        const itemExistente = carrito.find(item => item.nombre.toLowerCase() === nombre.toLowerCase());
        
        if (itemExistente) {
            itemExistente.cantidad += 1;
        } else {
            carrito.push({
                nombre: nombre,
                precio: precio,
                imagen: imagen,
                cantidad: 1
            });
        }
        
        guardarYActualizar();
        alert(`¡${nombre} se añadió a tu cesta!`);
    }

    /* ==========================================================================
       RENDERIZAR LISTA EN LA INTERFAZ
       ========================================================================== */
    function renderizarCarrito() {
        const mensajeVacio = document.getElementById('carrito-vacio-mensaje');
        const layoutLleno = document.getElementById('bloque-carrito-lleno-layout');
        const listaContenedor = document.getElementById('lista-productos-carrito');

        if (!listaContenedor) return;

        if (carrito.length === 0) {
            listaContenedor.innerHTML = '';
            if (mensajeVacio) mensajeVacio.style.display = 'block';
            if (layoutLleno) layoutLleno.style.display = 'none';
            const subtotal = document.getElementById('resumen-subtotal');
            const total = document.getElementById('resumen-total');
            if (subtotal) subtotal.innerText = "s/ 0.00";
            if (total) total.innerText = "s/ 0.00";
            actualizarBadgeCarrito();
            return;
        }

        if (mensajeVacio) mensajeVacio.style.display = 'none';
        if (layoutLleno) layoutLleno.style.display = 'flex';

        listaContenedor.innerHTML = '';

        carrito.forEach((item, index) => {
            const filaHTML = `
                <div class="tarjeta-producto-carrito">
                    <div class="carrito-producto-info">
                        <img src="${item.imagen || '/static/img/default.png'}" alt="${item.nombre}">
                        <div class="carrito-producto-detalles">
                            <h4>${item.nombre}</h4>
                            <span>s/ ${item.precio.toFixed(2)}</span>
                        </div>
                    </div>
                    
                    <div class="carrito-controles">
                        <div class="carrito-selector-cantidad">
                            <button class="btn-restar" data-index="${index}">-</button>
                            <span>${item.cantidad}</span>
                            <button class="btn-sumar" data-index="${index}">+</button>
                        </div>
                        
                        <button class="btn-eliminar-carrito" data-index="${index}">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>
                    </div>
                </div>
            `;
            listaContenedor.innerHTML += filaHTML;
        });

        asignarEventosBotones();
        calcularTotalesCarrito();
    }

    function asignarEventosBotones() {
        // Incrementar cantidad (+)
        document.querySelectorAll('.btn-sumar').forEach(btn => {
            btn.onclick = (e) => {
                const idx = e.currentTarget.getAttribute('data-index');
                carrito[idx].cantidad += 1;
                guardarYActualizar();
                renderizarCarrito();
            };
        });

        // Restar cantidad (-)
        document.querySelectorAll('.btn-restar').forEach(btn => {
            btn.onclick = (e) => {
                const idx = e.currentTarget.getAttribute('data-index');
                if (carrito[idx].cantidad > 1) {
                    carrito[idx].cantidad -= 1;
                } else {
                    carrito.splice(idx, 1);
                }
                guardarYActualizar();
                renderizarCarrito();
            };
        });

        // Eliminar producto por completo (Tachito)
        document.querySelectorAll('.btn-eliminar-carrito').forEach(btn => {
            btn.onclick = (e) => {
                const idx = e.currentTarget.getAttribute('data-index');
                carrito.splice(idx, 1);
                guardarYActualizar();
                renderizarCarrito();
            };
        });

        const btnWhatsapp = document.querySelector('.btn-confirmar-whatsapp');
        if (btnWhatsapp) {
            btnWhatsapp.onclick = enviarPedidoWhatsApp;
        }
    }

    function guardarYActualizar() {
        if (carrito.length === 0) {
            localStorage.removeItem('carrito-tienda');
        } else {
            localStorage.setItem('carrito-tienda', JSON.stringify(carrito));
        }
        actualizarBadgeCarrito();
    }

    function actualizarBadgeCarrito() {
        const badge = document.getElementById('contador-items-carrito-badge');
        if (badge) {
            const totalItems = carrito.reduce((acc, item) => acc + item.cantidad, 0);
            badge.innerText = totalItems;
        }
    }

    /* ==========================================================================
       CÁLCULO MATEMÁTICO PURO
       ========================================================================== */
    function calcularTotalesCarrito() {
        const subtotalElemento = document.getElementById('resumen-subtotal');
        const totalElemento = document.getElementById('resumen-total');

        if (!subtotalElemento || !totalElemento) return;

        // Suma basada en los objetos puros del almacenamiento, sin tocar textos de la interfaz
        let totalCalculado = 0;
        carrito.forEach(item => {
            totalCalculado += item.precio * item.cantidad;
        });
        
        subtotalElemento.innerText = `s/ ${totalCalculado.toFixed(2)}`;
        totalElemento.innerText = `s/ ${totalCalculado.toFixed(2)}`;
    }

    function enviarPedidoWhatsApp() {
        if (carrito.length === 0) return;

        const tuNumero = "51906984522"; // Tu número real de atención
        let mensaje = `🛒 *NUEVO PEDIDO - MINIMARKET DAMIR*\n\n`;
        
        carrito.forEach((item) => {
            mensaje += `▪️ *${item.cantidad}x* ${item.nombre} *(s/ ${item.precio.toFixed(2)} c/u)* → s/ ${(item.precio * item.cantidad).toFixed(2)}\n`;
        });

        let totalFinal = 0;
        carrito.forEach(item => { totalFinal += item.precio * item.cantidad; });

        mensaje += `\n💰 *Total a pagar:* s/ ${totalFinal.toFixed(2)}\n`;
        mensaje += `🚚 *Envío:* Gratis\n\n📌 _Espero la confirmación del pedido._`;

        window.open(`https://api.whatsapp.com/send?phone=${tuNumero}&text=${encodeURIComponent(mensaje)}`, '_blank');
    }
});
/* ========================================================================== 
   Dashboard Admin Interactivo
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    const tabla = document.getElementById('tabla-admin-datos');
    const buscador = document.getElementById('buscador-admin');
    if (!tabla) return;
    const filas = Array.from(tabla.querySelectorAll('tr')).slice(1);

    function limpiarActivo() {
        document.querySelectorAll('[data-admin-filter]').forEach(el => el.classList.remove('activo'));
        filas.forEach(fila => fila.classList.remove('fila-destacada-admin'));
    }

    function mostrarTodas() {
        filas.forEach(fila => fila.classList.remove('fila-oculta-admin'));
    }

    function aplicarFiltro(filtro) {
        mostrarTodas();
        if (!filtro || filtro === 'todos') return;
        filas.forEach(fila => {
            let mostrar = true;
            if (filtro === 'con-celular') mostrar = fila.dataset.celular === 'si';
            else if (filtro === 'con-direccion') mostrar = fila.dataset.direccion === 'si';
            else if (filtro === 'economicos') mostrar = parseFloat(fila.dataset.precio || '999') <= 5;
            else if (filtro.startsWith('inicial-')) mostrar = fila.dataset.inicial === filtro.replace('inicial-', '');
            else if (filtro.startsWith('pasillo-')) mostrar = fila.dataset.pasillo === filtro.replace('pasillo-', '');
            else if (filtro.startsWith('id-')) {
                mostrar = fila.dataset.id === filtro.replace('id-', '');
                if (mostrar) fila.classList.add('fila-destacada-admin');
            }
            else if (filtro.startsWith('nombre-')) {
                mostrar = (fila.dataset.nombre || '').toLowerCase().includes(filtro.replace('nombre-', '').toLowerCase());
                if (mostrar) fila.classList.add('fila-destacada-admin');
            }
            if (!mostrar) fila.classList.add('fila-oculta-admin');
        });
        tabla.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    document.querySelectorAll('[data-admin-filter]').forEach(elemento => {
        elemento.addEventListener('click', () => {
            limpiarActivo();
            elemento.classList.add('activo');
            aplicarFiltro(elemento.dataset.adminFilter);
        });
    });

    if (buscador) {
        buscador.addEventListener('input', () => {
            limpiarActivo();
            const texto = buscador.value.toLowerCase().trim();
            filas.forEach(fila => {
                fila.classList.toggle('fila-oculta-admin', texto && !fila.innerText.toLowerCase().includes(texto));
            });
        });
    }
});

/* ========================================================================== 
   WhatsApp Flotante, Pagos En Carrito Y Dashboard De Pagos
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
    if (!document.querySelector('.whatsapp-flotante')) {
        const enlace = document.createElement('a');
        enlace.href = 'https://api.whatsapp.com/send?phone=51906984522&text=Hola%20Minimarkt%20Damir%2C%20quiero%20hacer%20una%20consulta';
        enlace.target = '_blank';
        enlace.className = 'whatsapp-flotante';
        enlace.innerHTML = '<i class="fa-brands fa-whatsapp"></i>';
        document.body.appendChild(enlace);
    }

    const btnContinuar = document.getElementById('btn-continuar-compra');
    const panelPagos = document.getElementById('panel-metodos-pago');
    const btnCompletar = document.getElementById('btn-completar-pedido');
    const radiosPago = document.querySelectorAll('input[name="metodo_pago"]');

    if (btnContinuar && panelPagos) {
        btnContinuar.addEventListener('click', () => {
            panelPagos.style.display = 'block';
            btnContinuar.style.display = 'none';
        });
    }

    radiosPago.forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.campos-pago').forEach(caja => {
                caja.style.display = caja.dataset.pagoCampos.includes(radio.value) ? 'grid' : 'none';
            });
            if (btnCompletar) btnCompletar.style.display = 'flex';
        });
    });

    if (btnCompletar) {
        btnCompletar.addEventListener('click', () => {
            const metodo = document.querySelector('input[name="metodo_pago"]:checked');
            if (!metodo) {
                alert('Selecciona Un Método De Pago.');
                return;
            }
            const stats = JSON.parse(localStorage.getItem('metodos-pago-minimarkt')) || {};
            stats[metodo.value] = (stats[metodo.value] || 0) + 1;
            localStorage.setItem('metodos-pago-minimarkt', JSON.stringify(stats));
            localStorage.removeItem('carrito-tienda');
            localStorage.removeItem('carrito');
            localStorage.removeItem('productos-carrito');
            alert('Tu Pedido Fue Realizado Correctamente. Gracias Por Comprar En Minimarkt Damir.');
            window.location.href = '/';
        });
    }

    const stats = JSON.parse(localStorage.getItem('metodos-pago-minimarkt')) || {};
    const maximo = Math.max(1, ...Object.values(stats));
    document.querySelectorAll('[data-pago-total]').forEach(item => {
        const metodo = item.dataset.pagoTotal;
        item.textContent = stats[metodo] || 0;
    });
    document.querySelectorAll('[data-pago-bar]').forEach(barra => {
        const metodo = barra.dataset.pagoBar;
        const total = stats[metodo] || 0;
        barra.style.height = `${25 + (total / maximo) * 80}px`;
    });
});
