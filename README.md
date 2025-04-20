# Análisis de Precios y Ventas por Dealer

Este repositorio contiene un script en Python para procesar datos de precios y ventas por mes y por dealer (asociado de negocio), generar métricas clave, aplicar reglas de detección de oportunidades y exportar tanto tablas como una visualización a un archivo Excel.

---

## Tabla de Contenidos

- [Descripción General](#descripción-general)  
- [Requisitos](#requisitos)  
- [Estructura de Archivos](#estructura-de-archivos)  
- [Instalación](#instalación)  
- [Uso](#uso)  
- [Detalles del Procesamiento](#detalles-del-procesamiento)  
  - [1. Carga de Datos](#1-carga-de-datos)  
  - [2. Conversión de Fecha](#2-conversión-de-fecha)  
  - [3. Cálculo de Tamaño de Dealer](#3-cálculo-de-tamaño-de-dealer)  
  - [4. Métricas de Precio](#4-métricas-de-precio)  
  - [5. Métricas de Ventas (MoM y YoY)](#5-métricas-de-ventas-mom-y-yoy)  
  - [6. Percentil de Ventas](#6-percentil-de-ventas)  
  - [7. Aplicación de Reglas de Oportunidad](#7-aplicación-de-reglas-de-oportunidad)  
  - [8. Generación de Gráfico de Dispersión](#8-generación-de-gráfico-de-dispersión)  
  - [9. Exportación a Excel](#9-exportación-a-excel)  
- [Salida Generada](#salida-generada)  
- [Contribuciones](#contribuciones)  
- [Licencia](#licencia)  

---

## Descripción General

El script recorre los siguientes pasos principales:

1. **Lectura** de un archivo CSV con columnas de año, mes, cantidad vendida, precio unitario y código de producto.  
2. **Preprocesamiento** de fechas y limpieza de datos.  
3. **Clasificación** de dealers en Pequeño/Mediano/Grande según percentiles de ventas totales.  
4. **Cálculo** de métricas de precio (mediana por red, desviación porcentual) y métricas de ventas (crecimientos mes a mes y año a año).  
5. **Detección** de oportunidades mediante reglas basadas en precios elevados y bajas ventas.  
6. **Visualización** de la relación entre desviación de precio y percentil de ventas.  
7. **Exportación** de resultados y gráfico en un archivo Excel con múltiples hojas.

---

## Requisitos

- Python ≥ 3.7  
- pandas  
- numpy  
- matplotlib  
- openpyxl  

Puedes instalar las dependencias con:

```bash
pip install pandas numpy matplotlib openpyxl
```
---

## Estructura 

├── Price_Oportunity.py       # Script principal
├── requirements.txt          # Archivo de texto con las dependencias necesarias
└── README.md                 # Documentación (este archivo)

---

## Instalación
1. Clona este repositorio:
```bash
git clone https://github.com/tu_usuario/analisis-precios.git
cd analisis-precios
```
2. Crea un entorno virtual (opcional pero recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Instala dependencias.
```bash
pip install -r requirements.txt
```
---

## Uso
Edita la ruta de paths['df_prices'] dentro del script análisis_precios.py para apuntar a tu archivo CSV de datos y define también plot_path y la ruta de salida del Excel. Luego ejecuta:
```bash
python análisis_precios.py
```
---

## Detalles del Procesamiento
### 1. Carga de Datos
```python
df_prices = pd.read_csv(paths['df_prices'])
```
Se espera un CSV que contenga al menos las columnas:

- YEAR: Año (numérico)
- MONTH: Mes (número del 1 al 12)
- cantidad: Volumen de ventas (puede ser negativo o positivo)
- unit_price_amt: Precio unitario
- biz_assoc_id: Identificador del dealer
- part_nbr1: Código del producto

### 2. Conversión de Fecha

```python
df_prices['month_date'] = pd.to_datetime(
    df_prices['YEAR'].astype(str) + '-' +
    df_prices['MONTH'].astype(str).str.zfill(2) + '-01'
)
```

Crea la columna month_date con el primer día de cada mes.

### 3. Cálculo de Tamaño de Dealer
1. Suma absoluta de ventas (cantidad) por biz_assoc_id.
2. Cuantiles al 33% y 66% para clasificar:
  * Pequeño: hasta 33%
  * Mediano: 33%–66%
  * Grande: 66%–100%

```python
ventas_totales = df_prices.groupby('biz_assoc_id')['cantidad'] \
    .sum().abs().reset_index()
ventas_totales['dealer_size'] = pd.qcut(
    ventas_totales['cantidad'],
    q=[0, .33, .66, 1],
    labels=['Pequeño','Mediano','Grande']
)
```
```python
df_prices = df_prices.merge(ventas_totales[['biz_assoc_id','dealer_size']], on='biz_assoc_id')
```

### 4. Métricas de Precio
Precio Mediano por Red (precio_mediano_red): mediana de unit_price_amt por combinación de part_nbr1 y month_date.
Desviación de Precio (desviacion_precio): diferencia porcentual entre precio del dealer y la mediana de la red.

```python
df_prices['precio_mediano_red'] = df_prices \
    .groupby(['part_nbr1','month_date'])['unit_price_amt'] \
    .transform('median')
```
```python
df_prices['desviacion_precio'] = (
    (df_prices['unit_price_amt'] - df_prices['precio_mediano_red']) /
    df_prices['precio_mediano_red']
) * 100
```

### 5. Métricas de Ventas (MoM y YoY)
Calcula ventas absolutas (ventas_abs) como el valor absoluto de cantidad.
Crecimiento Mes a Mes (growth_ventas_mom): variación porcentual respecto al mes anterior dentro del mismo dealer y producto.
Crecimiento Año a Año (growth_ventas_yoy): variación porcentual respecto al mismo mes del año anterior.

```python
df_prices = df_prices.sort_values(['biz_assoc_id','part_nbr1','month_date'])
```
```python
df_prices['ventas_abs'] = df_prices['cantidad'].abs()
```
```python
df_prices['ventas_mes_anterior'] = df_prices \
    .groupby(['biz_assoc_id','part_nbr1'])['ventas_abs'] \
    .shift(1)
```
```python
df_prices['growth_ventas_mom'] = (
    (df_prices['ventas_abs'] - df_prices['ventas_mes_anterior']) /
    df_prices['ventas_mes_anterior']
) * 100
```

# Similar para YoY, empalmando con copia del df desplazada un año atrás
### 6. Percentil de Ventas
```python
df_prices['percentil_ventas'] = df_prices \
    .groupby(['part_nbr1','month_date'])['ventas_abs'] \
    .rank(pct=True) * 100
```
Posiciona cada dealer dentro de la distribución de ventas de ese producto/mes.

### 7. Aplicación de Reglas de Oportunidad
Se definen dos reglas:
#### Regla 1: Precio Alto + Ventas Bajas
  desviacion_precio > 20%
  percentil_ventas < 25%

#### Regla 2: Precio Alto + Caída Ventas
  desviacion_precio > 15%
  caída Month‑on‑Month (growth_ventas_mom < -10%) o caída Year‑on‑Year (growth_ventas_yoy < -20%)

```python
df['Regla_Activada'] = np.select(
    [cond1, cond2_mom|cond2_yoy],
    ['Regla 1: Precio Alto + Ventas Bajas','Regla 2: Precio Alto + Caída Ventas'],
    default='Sin Oportunidad'
)
```

### 8. Generación de Gráfico de Dispersión
  Eje X: desviacion_precio (%)
  Eje Y: percentil_ventas (%)
Puntos en rojo donde se activa alguna regla, gris en caso contrario.
Líneas de corte vertical en 15% y horizontal en 25% para visualizar “Zona de Oportunidad”.

plt.scatter(...)
plt.axvline(15, ...)
plt.axhline(25, ...)
plt.annotate('Zona de Oportunidad', ...)
plt.savefig(plot_path, dpi=150, bbox_inches='tight')

### 9. Exportación a Excel
Se crean tres hojas:
* Datos_Originales: DataFrame cargado y enriquecido con columnas intermedias.
* Analisis_Precios: Selección de columnas clave con métricas y regla activada.
* Visualización: Imagen del gráfico insertada.

```python
with pd.ExcelWriter(..., engine='openpyxl') as writer:
    ...
    worksheet = workbook.create_sheet('Visualización')
    worksheet.add_image(Image(plot_path), 'A1')
```

## Salida Generada
1. Archivo Excel: Analisis_Precios_Completo.xlsx
2. Contiene todas las hojas descritas.
3. Ideal para compartir con equipos de pricing o análisis comercial.

## Contribuciones
¡Contribuciones bienvenidas! Si encuentras errores o deseas mejorar el análisis:
Haz un fork de este repositorio.
Crea una rama con tu mejora: git checkout -b mejora-analisis.
Haz commit de tus cambios: git commit -m "Agrego nueva métrica de...".
Envía un pull request.

## Licencia
Este proyecto está bajo la MIT License.```
