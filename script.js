// Variables globales
let cursos = [];
let cursosFiltrados = [];

// Elementos del DOM
const searchInput = document.getElementById('search-input');
const clearSearchBtn = document.getElementById('clear-search');
const carouselTrack = document.getElementById('carousel-track');
const carouselContainer = document.querySelector('.carousel-container');
const prevBtn = document.querySelector('.carousel-btn.prev');
const nextBtn = document.querySelector('.carousel-btn.next');
const menuToggle = document.getElementById('menu-toggle');
const mobileMenu = document.getElementById('mobile-menu');
const searchToggle = document.getElementById('search-toggle');

// Cargar JSON y renderizar cursos
async function cargarCursos() {
    try {
        const response = await fetch('data/Cursos.json');
        cursos = await response.json();
        cursosFiltrados = [...cursos];
        renderizarCarrusel();
        actualizarBotones();
    } catch (error) {
        console.error('Error al cargar cursos:', error);
    }
}

// Crear elemento de curso (igual que antes)
function crearElementoCurso(curso) {
    const cursoDiv = document.createElement('div');
    cursoDiv.className = 'curso-card';
    cursoDiv.innerHTML = `
        <button class="reportar-btn" aria-label="Reportar link caído">Reportar</button>
        <img src="${curso.imagen}" alt="${curso.titulo}" loading="lazy">
        <h3>${curso.titulo}</h3>
        <p>${curso.descripcion}</p>
        <a href="${curso.enlace}" target="_blank" class="enlace-curso" aria-label="Acceder al curso ${curso.titulo}">Acceder</a>
    `;

    const reportBtn = cursoDiv.querySelector('.reportar-btn');
    if (reportBtn) {
        reportBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            alert('Funcionalidad de reporte próximamente disponible.');
        });
    }

    return cursoDiv;
}

// Renderizar carrusel (sin loop, sin transform)
function renderizarCarrusel() {
    carouselTrack.innerHTML = '';
    if (!cursosFiltrados || cursosFiltrados.length === 0) {
        actualizarBotones();
        return;
    }
    cursosFiltrados.forEach(curso => {
        const el = crearElementoCurso(curso);
        carouselTrack.appendChild(el);
    });
}

// Actualizar estado de botones (bloquear si ya está al principio o fin)
function actualizarBotones() {
    if (!carouselContainer) return;
    const scrollLeft = carouselContainer.scrollLeft;
    const maxScrollLeft = carouselContainer.scrollWidth - carouselContainer.clientWidth;
    prevBtn.disabled = scrollLeft <= 0;
    nextBtn.disabled = scrollLeft >= maxScrollLeft - 1; // con margen
}

// Función para desplazarse al hacer click en Prev/Next
function navegarCarrusel(direccion) {
    if (!carouselContainer) return;
    const scrollAmount = 300; // pixeles a desplazar por click (ajustable)
    if (direccion === 'next') {
        carouselContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    } else if (direccion === 'prev') {
        carouselContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    }
}

// Evento para actualizar botones al hacer scroll manual (por dedo)
if (carouselContainer) {
    carouselContainer.addEventListener('scroll', actualizarBotones);
}

// Filtrar cursos (mantener para búsqueda)
function filtrarCursos(query) {
    if (!query || !query.trim()) {
        cursosFiltrados = [...cursos];
    } else {
        const lowerQuery = query.toLowerCase();
        cursosFiltrados = cursos.filter(curso =>
            (curso.titulo || '').toLowerCase().includes(lowerQuery) ||
            (Array.isArray(curso.keywords) && curso.keywords.some(k => k.toLowerCase().includes(lowerQuery)))
        );
    }
    renderizarCarrusel();
    actualizarBotones();
}

// Limpiar búsqueda
function limpiarBusqueda() {
    if (searchInput) searchInput.value = '';
    cursosFiltrados = [...cursos];
    renderizarCarrusel();
    actualizarBotones();
}

// Toggle menú móvil
function toggleMenuMovil() {
    if (mobileMenu) mobileMenu.classList.toggle('open');
}

// Toggle barra de búsqueda móvil
function toggleBusquedaMovil() {
    const searchBar = document.querySelector('.search-bar');
    if (!searchBar) return;
    searchBar.classList.toggle('visible');
    if (searchBar.classList.contains('visible')) searchInput.focus();
}

// Event listeners
document.addEventListener('DOMContentLoaded', cargarCursos);

if (searchInput) {
    searchInput.addEventListener('input', (e) => filtrarCursos(e.target.value));
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') filtrarCursos(e.target.value);
    });
}
if (clearSearchBtn) clearSearchBtn.addEventListener('click', limpiarBusqueda);

if (prevBtn) prevBtn.addEventListener('click', () => navegarCarrusel('prev'));
if (nextBtn) nextBtn.addEventListener('click', () => navegarCarrusel('next'));
if (menuToggle) menuToggle.addEventListener('click', toggleMenuMovil);
if (searchToggle) searchToggle.addEventListener('click', toggleBusquedaMovil);

document.addEventListener('DOMContentLoaded', () => {
    const mobileMenu = document.getElementById('mobile-menu');
    if (mobileMenu) {
        const menuLinks = mobileMenu.querySelectorAll('nav a');
        menuLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('open');
            });
        });
    }
});
