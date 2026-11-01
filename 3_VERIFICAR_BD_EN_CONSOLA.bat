@echo off
cd /d "%~dp0"
chcp 65001 >nul
echo ============================================================================
echo   PUNTO 4: COMPROBACION DIRECTA DE REGISTROS EN UNIFORMADB
echo ============================================================================
python -c "from app.database import obtener_resumen_bd, listar_apartados_detallados, listar_prendas; r=obtener_resumen_bd(); print('Motor:', r['db_engine'], '| Origen:', r['db_path']); print('Conteos de tablas:', r['conteos']); print('\n--- APARTADOS ACTUALES EN LA BASE DE DATOS ---'); [print(f'Folio #{a[\"id_apartado\"]} | {a[\"tipo\"]} | Cliente: {a[\"cliente_nombre\"]} | Prenda: {a[\"prenda_modelo\"]} ({a[\"prenda_talla\"]}) | Precio: ${a[\"precio_aplicado\"]:.2f} | Abonado: ${a[\"total_pagado\"]:.2f} | Saldo: ${a[\"saldo_pendiente\"]:.2f} | Estado: {a[\"estado\"]}') for a in listar_apartados_detallados()]"
echo.
pause
