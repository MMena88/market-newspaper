# 🌌 Diario de Mercados Financieros

Un periódico financiero diario automatizado que recopila y analiza información clave de los mercados mundiales (acciones de megacapitalización como **NVIDIA**, criptomonedas con fuerte enfoque en **Bitcoin**, materias primas, divisas y rendimientos de bonos). Proporciona una opinión direccional clara sobre si el mercado subirá, bajará o se mantendrá lateral, soportado por un sofisticado análisis cuantitativo o por Inteligencia Artificial (Gemini).

---

## 🚀 Funcionalidades Clave

- **Análisis de Acciones Individuales**: Seguimiento diario y detección de catalizadores importantes para acciones líderes (NVIDIA `NVDA`, Apple `AAPL`, Microsoft `MSFT`, Tesla `TSLA`).
- **Enfoque Cripto (Bitcoin)**: Análisis específico de Bitcoin (`BTC-USD`) con una opinión direccional clara (**ALCISTA**, **BAJISTA** o **NEUTRAL/CONSOLIDACIÓN**).
- **Opinión del Mercado General**: Análisis estructurado sobre la dirección esperada a corto plazo del S&P 500, Nasdaq y Dow Jones.
- **Doble Motor de Análisis**:
  1. **Motor IA (Recomendado)**: Utiliza la API de Google Gemini para redactar un informe profesional y fluido en español.
  2. **Motor Determinista (Fallback)**: Si no se configura ninguna clave de API, utiliza un algoritmo cuantitativo propietario basado en retornos de activos, medias y momentum para generar el informe y evitar que el compilador falle.
- **Página Web de Aspecto Premium**: Interfaz moderna, oscura, responsiva, con estilo glassmorphism, micro-animaciones y un listado de archivos autogenerado.
- **Programador Diario**: Ejecución automatizada diaria a las **8:00 AM hora de Nueva York** (`America/New_York`), manejando de manera nativa los cambios de horario de verano/invierno.

---

## 📁 Estructura del Proyecto

```txt
NewsPaper/
│
├── CLAUDE.md                 # Especificaciones y directrices
├── README.md                 # Documentación del proyecto
├── requirements.txt          # Dependencias de Python
├── .env.example              # Plantilla de variables de entorno
├── .gitignore                # Exclusiones de control de versiones
│
├── scripts/
│   ├── generate_report.py    # Orquestador del flujo
│   ├── fetch_market_data.py  # Recopilación de datos y noticias
│   ├── analyze_market.py     # Lógica de análisis (IA / Reglas)
│   └── render_report.py      # Generador de archivos HTML/Markdown
│
├── reports/                  # Archivo histórico en formato Markdown
│   └── YYYY-MM-DD.md
│
└── public/                   # Carpeta del sitio web estático
    ├── index.html            # Página de la última edición (compilada)
    ├── app.css               # Estilos obsidian-violet glassmorphic
    ├── app.js                # Lógica del frontend y menú del archivo histórico
    ├── templates/
    │   └── index_template.html # Plantilla HTML base
    └── reports/              # Archivo histórico en HTML e índice JSON
        ├── archive.json      # Catálogo de reportes disponibles
        └── YYYY-MM-DD.html
```

---

## 🛠️ Instalación y Configuración

### 1. Requisitos Previos
Asegúrate de tener instalado Python 3.10 o superior.

### 2. Clonar e Instalar Dependencias
Instala las bibliotecas requeridas ejecutando en la consola de tu sistema:
```bash
pip install -r requirements.txt
```

### 3. Configurar Clave de API (Opcional)
Para obtener el análisis avanzado de Inteligencia Artificial:
1. Copia el archivo `.env.example` y renómbralo a `.env`:
   ```bash
   copy .env.example .env
   ```
2. Abre el archivo `.env` y coloca tu clave de API de Gemini:
   ```env
   GEMINI_API_KEY=tu_clave_api_aqui
   ```
*Nota: Si dejas el archivo `.env` vacío o no creas el archivo, el proyecto funcionará con normalidad utilizando el motor cuantitativo de respaldo.*

---

## 🏃 Ejecución Manual

Para generar o actualizar el periódico financiero de hoy de manera inmediata, ejecuta:

```bash
python scripts/generate_report.py --force
```

- El flag `--force` es necesario si ejecutas el script a una hora distinta a las 8:00 AM de Nueva York.
- Una vez finalizado el script, abre el archivo `public/index.html` en cualquier navegador web para ver el periódico diario.

---

## ⏰ Automatización Diaria (GitHub Actions)

El archivo `.github/workflows/daily-report.yml` define la ejecución automatizada:

1. Se ejecuta cada hora (cron: `0 * * * *`).
2. El script `generate_report.py` verifica la hora local en Nueva York (`America/New_York`).
3. Si la hora es exactamente las **8:00 AM**, el script procede a compilar el periódico del día. De lo contrario, finaliza de manera segura y silenciosa.
4. Los nuevos archivos generados se confirman y se suben directamente al repositorio de GitHub.

### Configuración en GitHub
Para que funcione el análisis con IA en el servidor automatizado:
1. Ve a la configuración de tu repositorio en GitHub: **Settings > Secrets and variables > Actions**.
2. Añade un **New repository secret** con el nombre `GEMINI_API_KEY` y el valor de tu clave API de Gemini.

---

## 🌐 Despliegue de la Página Web

Dado que el periódico genera páginas estáticas puras en la carpeta `public`, el despliegue es muy sencillo:

### GitHub Pages (Recomendado y Gratuito)
1. Ve a la configuración del repositorio en GitHub: **Settings > Pages**.
2. En **Build and deployment > Source**, selecciona **Deploy from a branch**.
3. Elige la rama (generalmente `main`) y selecciona la carpeta `/public` (o la raíz del proyecto si configuras el punto de entrada, aunque es mejor desplegar la carpeta `/public`).
4. ¡Listo! Tu periódico estará disponible públicamente y se actualizará automáticamente todos los días.

---

## 🔍 Solución de Problemas

### 1. El script finaliza sin generar ningún archivo
**Causa**: Estás ejecutando el script fuera de las 8:00 AM de Nueva York.
**Solución**: Añade el flag `--force` en tu comando: `python scripts/generate_report.py --force`.

### 2. Error `ModuleNotFoundError`
**Causa**: Las dependencias de Python no están instaladas en tu entorno.
**Solución**: Ejecuta `pip install -r requirements.txt`.

### 3. Error en la clave de la API de Gemini
**Causa**: La clave API está mal copiada o no tiene permisos.
**Solución**: Verifica que la clave en el archivo `.env` sea correcta o déjala en blanco para que el sistema use el motor de respaldo basado en reglas y datos directos de Yahoo Finance.

---

## ⚠️ Descargo de Responsabilidad (Disclaimer)

Toda la información proporcionada en este periódico financiero diario se recopila de fuentes públicas y se procesa mediante algoritmos e Inteligencia Artificial con fines educativos e ilustrativos. Este periódico **no representa asesoría financiera**.
