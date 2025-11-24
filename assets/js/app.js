// Variables globales
let contenido = {};
let seccionActual = '';
let elementosFiltrados = [];

// ...existing code...
async function cargarContenido() {
    const posiblesRutas = [
        'assets/js/contenido.json',  // ruta correcta desde index.html
        '/contenido.json',        // raíz del servidor
        '/data/contenido.json',   // common: carpeta data en raíz
        '../../contenido.json',   // desde assets/js -> subir dos niveles
        '../contenido.json',      // subir un nivel
        'contenido.json'          // misma carpeta (fallback)
    ];

    let response = null;
    let rutaIntentada = null;
    const intentos = [];

    for (const ruta of posiblesRutas) {
        try {
            rutaIntentada = ruta;
            response = await fetch(ruta);
            intentos.push({ ruta, ok: response.ok, status: response.status });
            if (response.ok) break;
        } catch (err) {
            intentos.push({ ruta, ok: false, error: err.message });
            // continuar probando otras rutas
        }
    }

    try {
        if (!response || !response.ok) {
            const detalles = intentos.map(i => {
                if (i.ok) return `${i.ruta} -> OK (${i.status})`;
                if (i.status) return `${i.ruta} -> HTTP ${i.status}`;
                return `${i.ruta} -> ERROR (${i.error || 'no response'})`;
            }).join('\n');
            const mensajeUI = 'Error al cargar el contenido. Verifica que contenido.json exista y que estés sirviendo el proyecto por HTTP. Rutas probadas:\n' + detalles;
            mostrarError('Error al cargar el contenido. Verifica que contenido.json exista y que estés sirviendo el proyecto por HTTP. Revisa la consola para más detalles.');
            console.error('Error cargando JSON. Rutas probadas:\n' + detalles);
            return;
        }

        contenido = await response.json();
        inicializarApp();
    } catch (error) {
        mostrarError('Error al procesar contenido.json. Revisa la consola para más detalles.');
        console.error('Error parseando JSON:', error);
    }
}

// Función para inicializar la aplicación
function inicializarApp() {
    construirMenu();
    const isSobrePage = window.location.pathname.includes('sobre-nosotros.html');
    if (!isSobrePage) {
        manejarHash();
        window.addEventListener('hashchange', manejarHash);
        document.getElementById('search-input').addEventListener('input', filtrarElementos);
        document.getElementById('sort-select').addEventListener('change', ordenarElementos);
    }
    const hamburger = document.getElementById('hamburger');
    if (hamburger) {
        hamburger.addEventListener('click', toggleMenu);
    }
    agregarFooter();
}

// Función para construir el menú de navegación
function construirMenu() {
    const navMenu = document.getElementById('nav-menu');
    const ul = document.createElement('ul');
    const secciones = Object.keys(contenido).sort();
    // Mover "sobre_nosotros" al frente
    const indexSobre = secciones.indexOf('sobre_nosotros');
    if (indexSobre > -1) {
        secciones.splice(indexSobre, 1);
        secciones.unshift('sobre_nosotros');
    }

    const isSobrePage = window.location.pathname.includes('sobre-nosotros.html');

    secciones.forEach(seccion => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        if (seccion === 'sobre_nosotros') {
            a.href = 'sobre-nosotros.html'; // Navigate to landing page
            a.textContent = 'Sobre nosotros';
        } else {
            a.href = isSobrePage ? `index.html#/${seccion}` : `#/${seccion}`;
            a.textContent = seccion.charAt(0).toUpperCase() + seccion.slice(1);
        }
        a.addEventListener('click', () => {
            // Cerrar el menú hamburguesa al hacer clic en un enlace
            navMenu.classList.remove('open');
        });
        li.appendChild(a);
        ul.appendChild(li);
    });

    navMenu.appendChild(ul);
}

// Función para manejar el hash de la URL
function manejarHash() {
    const hash = window.location.hash.substring(2); // Remover #/
    const secciones = Object.keys(contenido);
    if (secciones.includes(hash)) {
        cambiarSeccion(hash);
    } else if (secciones.length > 0) {
        cambiarSeccion(secciones[0]);
        window.location.hash = `/${secciones[0]}`;
    }
}

// Función para cambiar de sección
function cambiarSeccion(seccion) {
    seccionActual = seccion;
    actualizarMenuActivo();
    cargarElementos();
    // Cerrar el menú hamburguesa después de cambiar de sección
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.remove('open');
}

// Función para actualizar el menú activo
function actualizarMenuActivo() {
    const links = document.querySelectorAll('#nav-menu a');
    links.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#/${seccionActual}`) {
            link.classList.add('active');
        }
    });
}

// Función para cargar y mostrar elementos
function cargarElementos() {
    const elementos = contenido[seccionActual] || [];
    elementosFiltrados = [...elementos];
    ordenarElementos();
    filtrarElementos();
    actualizarContador();
}

// Función para ordenar elementos
function ordenarElementos() {
    const orden = document.getElementById('sort-select').value;
    elementosFiltrados.sort((a, b) => {
        const tituloA = a.titulo.toLowerCase();
        const tituloB = b.titulo.toLowerCase();
        if (orden === 'asc') {
            return tituloA.localeCompare(tituloB);
        } else {
            return tituloB.localeCompare(tituloA);
        }
    });
    renderizarElementos();
}

// Función para filtrar elementos
function filtrarElementos() {
    const query = document.getElementById('search-input').value.toLowerCase();
    const filtrados = elementosFiltrados.filter(elemento =>
        elemento.titulo.toLowerCase().includes(query) ||
        elemento.descripcion.toLowerCase().includes(query)
    );
    renderizarElementos(filtrados);
    actualizarContador(filtrados.length);
}

// Función para renderizar elementos
function renderizarElementos(elementos = elementosFiltrados) {
    const content = document.getElementById('content');
    content.innerHTML = '';

    if (elementos.length === 0) {
        const message = document.createElement('div');
        message.className = 'message empty';
        message.textContent = 'No hay elementos en esta sección.';
        content.appendChild(message);
        return;
    }

    const fragment = document.createDocumentFragment();
    elementos.forEach(elemento => {
        const card = crearTarjeta(elemento);
        fragment.appendChild(card);
    });
    content.appendChild(fragment);
}



// Función para crear una tarjeta de elemento
function crearTarjeta(elemento) {
    const card = document.createElement('div');
    card.className = 'card';

    // Solo agregar imagen si hay portada
    if (elemento.portada) {
        const img = document.createElement('img');
        img.src = `assets/img/${elemento.portada}`;
        img.alt = `Portada de ${elemento.titulo}`;
        card.appendChild(img);
    }

    const cardContent = document.createElement('div');
    cardContent.className = 'card-content';

    const h3 = document.createElement('h3');
    h3.textContent = elemento.titulo;
    cardContent.appendChild(h3);

    const p = document.createElement('p');
    p.textContent = elemento.descripcion;
    cardContent.appendChild(p);

    if (elemento.enlace) {
        const a = document.createElement('a');
        a.href = elemento.enlace;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = 'Ver recurso';
        cardContent.appendChild(a);
    }

    card.appendChild(cardContent);
    return card;
}

// Función para actualizar el contador de elementos
function actualizarContador(cantidad = elementosFiltrados.length) {
    document.getElementById('item-count').textContent = `Elementos: ${cantidad}`;
}

// Función para mostrar errores
function mostrarError(mensaje) {
    const content = document.getElementById('content');
    content.innerHTML = '';
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message error';
    errorDiv.textContent = mensaje;
    content.appendChild(errorDiv);
}

// Función para agregar el footer (si no existe)
function agregarFooter() {
    // Esta función ya está definida en el código original, pero si no, aquí va
    // Asumiendo que está definida, no la redefino
    // Si no existe, puedes agregar aquí
    // Para este caso, asumimos que existe
}

// Función para alternar el menú hamburguesa
function toggleMenu() {
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.toggle('open');
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', cargarContenido);
