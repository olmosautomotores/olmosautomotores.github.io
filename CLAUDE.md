# OLMOSWEB — Página de autos en venta de Olmos Automotores

- Responder SIEMPRE en español rioplatense, lenguaje simple. El usuario no es programador.
- Marca: Olmos Automotores (IG @olmos.automotores), Mendoza. WhatsApp/tel 261 554-0670 → `5492615540670`.
  Material de marca original en `~/Desktop/OLMOS AUTOMOTORES` (logos, tarjeta). Estilo: negro + franjas naranja→rojo, títulos en cursiva mayúscula.
- Proyecto separado de CUBIERTASMDZ y AUTOPARTESMDZ (no enlazar entre sí).
- Creado 2026-11-05. Todavía NO publicado (falta que el usuario elija dónde: ver "Publicar").

## Estructura
- `autos.json` = fuente de verdad (datos del negocio + lista de autos). Todo lo que está ahí es PÚBLICO.
- `fotos/<id>/N.jpg` (1080px), `fotos/<id>/m/` (720px, tarjetas), `fotos/<id>/t/` (miniaturas). La 1 es la portada.
- `index.html`, `a/<id>/index.html`, `sitemap.xml` — los genera el build. NO editarlos a mano.
- `assets/` (style.css, app.js, logos, og-olmos.jpg). Si se cambia CSS/JS, subir `VER` en tools/build.py.
- `_ig/` fotos bajadas del Instagram (no se publican), `fuente/` material original (no se publica).

## Comandos
```
cd ~/Desktop/OLMOSWEB
.venv/bin/python tools/build.py build                 # fotos nuevas + páginas
.venv/bin/python tools/build.py fotos <id>            # re-procesar fotos de un auto (si cambió fotos_origen)
.venv/bin/python tools/build.py publicar "mensaje"    # build + git commit + push
```
Ver en local: `.venv/bin/python -m http.server 8767 --bind 127.0.0.1` → http://127.0.0.1:8767/

## Campos de cada auto (autos.json)
`id` (ej. "ford-fiesta-kinetic-2017", es el link a/<id>/), `marca`, `modelo`, `version`, `anio`, `km`, `motor`, `combustible`,
`caja`, `traccion` (opcional), `carroceria` (SUV, Hatchback, Sedán, Pick-up… arma los botones de filtro), `color` (opcional),
`precio` (número; null → "Consultar"), `moneda` (ARS|USD), `estado` (disponible | reservado → cinta | vendido → se oculta del listado, el link avisa "ya se vendió"),
`fecha` (ingreso, ordena "más recientes"), `destacados` (lista), `descripcion`, `fotos_origen` (rutas; la primera = portada).
- No inventar datos. Si falta algo, preguntar o dejar el campo afuera.

## Cargar un auto nuevo
1. Fotos: copiarlas a `_ig/` (o usar rutas absolutas) y ponerlas en `fotos_origen` (portada primero: una foto limpia de 3/4 frente).
2. Agregar el auto en `autos.json` → `build` → revisar en local → `publicar`.
- Desde Instagram: el navegador interno está logueado. Se baja con la API interna
  `/api/v1/media/<id>/info/` (id = shortcode en base64 → número) y un servidor local que recibe la lista de URLs (ver sesión 2026-11-05).
  Ojo: los carruseles traen fotos repetidas → comparar con `md5 -r`.

## Publicar
- Plan: GitHub Pages. URL provisoria configurada en `autos.json` → `negocio.url` = https://cubiertasmdz.github.io/olmos/ (repo a crear `cubiertasmdz/olmos`).
  Si el usuario prefiere otra cuenta o dominio propio (ej. olmosautomotores.com.ar), cambiar `negocio.url` y rebuild.

## Estado
- 2026-11-05: cargados desde el Instagram 4 autos: Fiesta Kinetic 2017 ($15.000.000), EcoSport XLT Plus 2012 ($10.900.000),
  Audi Q3 2013 ($25.900.000), SW4 SRV 2007 (US$ 20.000). Suzuki Fun no (vendido). Falta confirmar con el usuario si siguen todos a la venta.
  Combustible de Q3 (nafta) y SW4 (diésel) puesto por ser de fábrica; el resto sale de los posts.
