import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import sys
from openpyxl.drawing.image import Image

paths = {
    'df_prices': r"",
}

try:
    # Carga y preprocesamiento original
    df_prices = pd.read_csv(paths['df_prices'])
    
    # 1. Convertir mes y año a datetime
    df_prices['month_date'] = pd.to_datetime(
        df_prices['YEAR'].astype(str) + '-' + 
        df_prices['MONTH'].astype(str).str.zfill(2) + '-01'
    )
    
    # 2. Calcular tamaño del dealer
    ventas_totales = df_prices.groupby('biz_assoc_id')['cantidad'].sum().abs().reset_index()
    ventas_totales['dealer_size'] = pd.qcut(
        ventas_totales['cantidad'],
        q=[0, 0.33, 0.66, 1],
        labels=['Pequeño', 'Mediano', 'Grande']
    )
    df_prices = df_prices.merge(ventas_totales[['biz_assoc_id', 'dealer_size']], on='biz_assoc_id')
    
    # 3. Métricas de precio
    df_prices['precio_mediano_red'] = df_prices.groupby(['part_nbr1', 'month_date'])['unit_price_amt'].transform('median')
    df_prices['desviacion_precio'] = ((df_prices['unit_price_amt'] - df_prices['precio_mediano_red']) / 
                                     df_prices['precio_mediano_red']) * 100
    
    # 4. Métricas de ventas
    df_prices = df_prices.sort_values(['biz_assoc_id', 'part_nbr1', 'month_date'])
    df_prices['ventas_abs'] = df_prices['cantidad'].abs()
    
    # Crecimiento MoM
    df_prices['ventas_mes_anterior'] = df_prices.groupby(['biz_assoc_id', 'part_nbr1'])['ventas_abs'].shift(1)
    df_prices['growth_ventas_mom'] = ((df_prices['ventas_abs'] - df_prices['ventas_mes_anterior']) / 
                                     df_prices['ventas_mes_anterior']) * 100
    
    # Crecimiento YoY
    df_prices['month_last_year'] = df_prices['month_date'] - pd.DateOffset(years=1)
    df_yoy = df_prices.merge(
        df_prices[['biz_assoc_id', 'part_nbr1', 'month_date', 'ventas_abs']],
        left_on=['biz_assoc_id', 'part_nbr1', 'month_last_year'],
        right_on=['biz_assoc_id', 'part_nbr1', 'month_date'],
        suffixes=('', '_last_year')
    )
    df_yoy['growth_ventas_yoy'] = ((df_yoy['ventas_abs'] - df_yoy['ventas_abs_last_year']) / 
                                  df_yoy['ventas_abs_last_year']) * 100
    df_prices = df_prices.merge(
        df_yoy[['biz_assoc_id', 'part_nbr1', 'month_date', 'growth_ventas_yoy']],
        on=['biz_assoc_id', 'part_nbr1', 'month_date'], 
        how='left'
    )
    
    # 5. Percentil de ventas
    df_prices['percentil_ventas'] = df_prices.groupby(['part_nbr1', 'month_date'])['ventas_abs'].rank(pct=True) * 100
    
    # 6. Aplicar reglas
    def aplicar_reglas(df):
        condicion_regla1 = (
            (df['desviacion_precio'] > 20) &
            (df['percentil_ventas'] < 25))
        
        condicion_regla2_mom = (
            (df['desviacion_precio'] > 15) &
            (df['growth_ventas_mom'] < -10))
        
        condicion_regla2_yoy = (
            (df['desviacion_precio'] > 15) &
            (df['growth_ventas_yoy'] < -20))
        
        df['Regla_Activada'] = np.select(
            [condicion_regla1, condicion_regla2_mom | condicion_regla2_yoy],
            ['Regla 1: Precio Alto + Ventas Bajas', 'Regla 2: Precio Alto + Caída Ventas'],
            default='Sin Oportunidad'
        )
        return df
    
    df_final = aplicar_reglas(df_prices)
   
    # Ordenar columnas
    columnas_reporte = [
        'biz_assoc_id', 'dealer_size', 'part_nbr1', 'month_date',
        'MONTH', 'YEAR', 'unit_price_amt', 'precio_mediano_red',
        'desviacion_precio', 'cantidad', 'ventas_abs', 'percentil_ventas',
        'growth_ventas_mom', 'growth_ventas_yoy', 'Regla_Activada'
    ]
    
    # Crear gráfico
    plt.figure(figsize=(10, 6))
    plt.scatter(
        x=df_final['desviacion_precio'],
        y=df_final['percentil_ventas'],
        c=np.where(df_final['Regla_Activada'] != 'Sin Oportunidad', 'red', 'lightgrey'),
        alpha=0.6,
        edgecolors='w',
        linewidth=0.5
    )
    plt.title('Relación entre Desviación de Precios y Percentil de Ventas', fontsize=14)
    plt.xlabel('Desviación de Precio (%)', fontsize=12)
    plt.ylabel('Percentil de Ventas (%)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.axvline(15, color='orange', linestyle='--', linewidth=1)
    plt.axhline(25, color='orange', linestyle='--', linewidth=1)
    plt.annotate('Zona de Oportunidad', xy=(30, 10), 
                xytext=(40, 5), 
                arrowprops=dict(facecolor='red', shrink=0.05),
                color='red', fontsize=10)
    
    plot_path = r""
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()

    # Generar Excel
    with pd.ExcelWriter(
        r"", 
        engine='openpyxl'
    ) as writer:
        df_prices.to_excel(writer, sheet_name='Datos_Originales', index=False)
        df_final[columnas_reporte].to_excel(writer, sheet_name='Analisis_Precios', index=False)
        
        workbook = writer.book
        worksheet = workbook.create_sheet('Visualización')
        img = Image(plot_path)
        worksheet.add_image(img, 'A1')
    
    print("Proceso completado exitosamente. Archivo generado: Analisis_Precios_Completo.xlsx")

except Exception as e:
    print(f"Error en el proceso: {str(e)}")
    sys.exit(1)