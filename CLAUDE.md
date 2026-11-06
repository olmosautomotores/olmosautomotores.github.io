# OLMOSWEB — Página de autos en venta de Olmos Automotores

- Responder SIEMPRE en español rioplatense, lenguaje simple. El usuario no es programador.
- Marca: Olmos Automotores (IG @olmos.automotores), Mendoza. WhatsApp/tel 261 554-0670 → `5492615540670`.
  Material de marca original en `~/Desktop/OLMOS AUTOMOTORES` (logos, tarjeta). Estilo: negro + franjas naranja→rojo, títulos en cursiva mayúscula.
- Proyecto separado de CUBIERTASMDZ y AUTOPARTESMDZ (no enlazar entre sí).
- Creado 2026-11-05. Publicada en **https://olmosautomotores.github.io/** — cuenta GitHub PROPIA `olmosautomotores`, repo `olmosautomotores/olmosautomotores.github.io`.
  PEDIDO: nada bajo cubiertasmdz (son negocios distintos). La copia vieja cubiertasmdz/olmos: Pages apagado y repo privado (2026-11-05);
  borrarlo del todo necesita el permiso delete_repo o hacerlo el usuario en GitHub (Settings → Delete).
- gh tiene 2 cuentas; la ACTIVA debe quedar `cubiertasmdz` (la usan CUBIERTASMDZ y AUTOPARTESMDZ). Esta carpeta sube sola con la
  cuenta de Olmos: `.git/config` local tiene un credential.helper que pide `gh auth token -u olmosautomotores`. No hace falta cambiar de cuenta.
  Para comandos `gh` sobre este repo: `GH_TOKEN=$(gh auth token -u olmosautomotores) gh ...`.

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
`equipamiento` (grupos → lista: Seguridad, Confort, Tecnología, Exterior, Mecánica, Otros; se muestra en la ficha).
- No inventar datos. Si falta algo, preguntar o dejar el campo afuera.
- Equipamiento cargado 2026-11-05 con: lo que dice el post + lo visible en las fotos + equipamiento de serie de la versión que es seguro
  (ABS y airbags frontales obligatorios en Argentina desde 2014). Conservador: ante la duda, no se pone. Pendiente que el usuario lo revise.

## Etiquetas de las tarjetas (automáticas, máx. 3)
- "Nuevo ingreso" si `fecha` tiene ≤ 21 días (DIAS_NUEVO en build.py) → rebuild/publicar de vez en cuando para que se vaya sola.
- "GNC" si el combustible dice GNC; "4x4" / "Quattro" según `traccion`; "Único dueño" si `unico_dueno: true`; extras en `etiquetas: [...]`.

## Diseño (2026-11-05)
- Portada ROTATIVA (pedido 2026-11-05): va pasando por todos los autos no vendidos cada 6 s, arranca en uno al azar, con etiqueta
  "Marca Modelo Año · Ver auto". Las fotos salen solas de la portada de cada auto (`assets/hero/<id>.jpg`, recorte apaisado).
  Si el recorte queda mal, ajustar `hero_y` en el auto (0 = arriba de la foto; por defecto 0.28) y rebuild.
- Entregas van JUSTO DEBAJO del catálogo (pedido 2026-11-05), después servicios, formularios y contacto. El contador dice `negocio.entregas_texto` ("+20 autos entregados", pedido del usuario).
- Tarjetas de a 3 (compu), 2 (tablet), 1 (celular). Ficha en celular: barra fija abajo con precio + WhatsApp al pasar los botones.
- Animaciones suaves: la portada con CSS; el resto aparece al bajar (solo lo que está fuera de pantalla al cargar).
- Ojo: con el panel del navegador interno OCULTO las animaciones se ven congeladas en las capturas; no es un error.

## Otras secciones del inicio
- Formularios `#cotizar` (pestañas "Cotizá tu auto" y "Te lo buscamos"): no hay servidor; al enviar arma el mensaje y abre WhatsApp (wa.me).
- Entregas `#entregas`: tira horizontal chica con visor. `autos.json` → `entregas` = [{auto, foto}]; fotos originales en `fuente/entregas/`
  (copiadas de `~/Desktop/OLMOS AUTOMOTORES/DESTACADAS CONTENIDO/ENTREGAS - VENTAS`, 6.png a 17.png). Se procesan a `entregas/` (810px) y `entregas/t/`.
  Si cambia la cantidad, el build las regenera. Para sumar una: agregarla al final de la lista.

## Cargar un auto nuevo
1. Fotos: copiarlas a `_ig/` (o usar rutas absolutas) y ponerlas en `fotos_origen` (portada primero: una foto limpia de 3/4 frente).
2. Agregar el auto en `autos.json` → `build` → revisar en local → `publicar`.
- Desde Instagram: el navegador interno está logueado. Se baja con la API interna
  `/api/v1/media/<id>/info/` (id = shortcode en base64 → número) y un servidor local que recibe la lista de URLs (ver sesión 2026-11-05).
  Ojo: los carruseles traen fotos repetidas → comparar con `md5 -r`.

## Publicar
- GitHub Pages, `negocio.url` = https://olmosautomotores.github.io/. Tarda 1-2 minutos en mostrar cambios.
  Si el usuario prefiere otra cuenta o dominio propio (ej. olmosautomotores.com.ar), cambiar `negocio.url` y rebuild.

## Estado
- Stock al 2026-11-05 (confirmado por el usuario: "esos son el total de autos", 6): Fiesta Kinetic 2017, EcoSport XLT Plus 2012,
  Audi Q3 2013, SW4 SRV 2007 (US$), Toyota Corolla SEG 2018 ($26.800.000, 171.000 km según el texto del post; la placa de la foto dice 170.000)
  y Chevrolet Cruze LT 2015 negro ($14.300.000). Datos sacados de los posts de Instagram de cada auto.
- Cuando el usuario nombra autos para cargar, se SUMAN a los que ya están (no reemplazar) salvo que diga lo contrario.
- `portada_pos` (opcional): encuadre de la portada en la tarjeta, ej. "center 100%" (el Cruze tiene la placa de datos arriba en la foto 1).
