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
