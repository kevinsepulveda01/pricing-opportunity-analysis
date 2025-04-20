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

├── análisis_precios.py       # Script principal
├── datos/                    # Carpeta para datos de entrada y salida
│   ├── precios.csv           # CSV de ejemplo de precios y ventas
│   └── Analisis_Precios_Completo.xlsx  # Salida generada
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
df_prices = pd.read_csv(paths['df_prices'])
Se espera un CSV que contenga al menos las columnas:

- YEAR: Año (numérico)
- MONTH: Mes (número del 1 al 12)
- cantidad: Volumen de ventas (puede ser negativo o positivo)
- unit_price_amt: Precio unitario
- biz_assoc_id: Identificador del dealer
- part_nbr1: Código del producto

### 2. Conversión de Fecha
df_prices['month_date'] = pd.to_datetime(
    df_prices['YEAR'].astype(str) + '-' +
    df_prices['MONTH'].astype(str).str.zfill(2) + '-01'
)

Crea la columna month_date con el primer día de cada mes.

### 3. Cálculo de Tamaño de Dealer
1. Suma absoluta de ventas (cantidad) por biz_assoc_id.
2. Cuantiles al 33% y 66% para clasificar:
  * Pequeño: hasta 33%
  * Mediano: 33%–66%
  * Grande: 66%–100%

ventas_totales = df_prices.groupby('biz_assoc_id')['cantidad'] \
    .sum().abs().reset_index()
ventas_totales['dealer_size'] = pd.qcut(
    ventas_totales['cantidad'],
    q=[0, .33, .66, 1],
    labels=['Pequeño','Mediano','Grande']
)
df_prices = df_prices.merge(ventas_totales[['biz_assoc_id','dealer_size']], on='biz_assoc_id')

---
