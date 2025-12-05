# Manual de Usuario: Gestor de Validaciones y Reportes

## 1. ¿Para qué sirve esta herramienta?

¡Bienvenido! Esta es una herramienta automática diseñada para simplificar tu trabajo diario. Su principal objetivo es 
leer varios archivos de Excel que contienen información de pólizas de seguros de **Rímac** y **Pacífico**, cruzarlos con datos de sistemas internos como **SICS** y **SharePoint**, y generar reportes consolidados y limpios.

En resumen, la herramienta hace lo siguiente por ti:
1.  **Lee** los archivos de Excel que tú le proporcionas.
2.  **Limpia y prepara** los datos automáticamente.
3.  **Cruza la información** para ver qué pólizas se encuentran en cada sistema.
4.  **Aplica reglas de negocio** (como asignar responsables o marcar observaciones) para enriquecer los datos.
5.  **Genera un reporte final** en Excel, listo para que lo puedas analizar.

## 2. Antes de empezar: ¿Qué necesitas?

Para que la herramienta funcione correctamente, solo debes asegurarte de dos cosas:

-   Tener los **archivos de Excel necesarios**.
-   Colocar cada archivo en su **carpeta correspondiente**.

¡Eso es todo! No necesitas instalar nada ni configurar nada complicado.

## 3. Estructura de Carpetas: ¿Dónde va cada cosa?

El proyecto tiene una carpeta principal llamada `src/app/data` que se divide en dos: `input` (para tus archivos) y `output` (donde la herramienta dejará los resultados).

```
GestorDeValidaciones/
└── src/
    └── app/
        └── data/
            ├── input/         <-- AQUÍ PONES TUS ARCHIVOS
            │   ├── PreparaciónPacífico/
            │   │   └── Anulados/
            │   ├── PreparaciónRimac/
            │   ├── PreparaciónSharepoint/
            │   └── PreparaciónSics/
            │
            └── output/        <-- AQUÍ ENCONTRARÁS LOS RESULTADOS
                ├── Pacífico/
                │   └── PacificoAnulado/
                ├── PacíficoIntegrado/
                └── Rimac/
```

### Carpeta `input`: Tus archivos de trabajo

Aquí es donde debes colocar los reportes que descargas de los diferentes sistemas. Es **muy importante** que cada archivo vaya en su carpeta específica.

| Carpeta | Archivo que debes poner |
| :--- | :--- |
| **`input/PreparaciónPacífico/`** | El reporte de pólizas descargado de **Pacífico**. |
| **`input/PreparaciónPacífico/Anulados/`** | El reporte de pólizas anuladas de **Pacífico**. |
| **`input/PreparaciónRimac/`** | El reporte de pagos vencidos de **Rímac**. |
| **`input/PreparaciónSharepoint/`** | El archivo de seguimiento de renovaciones de **SharePoint**. |
| **`input/PreparaciónSics/`** | El reporte de pólizas por filtro de **SICS**. |

**Importante:** La herramienta está diseñada para leer el archivo **más reciente** que encuentre en cada carpeta. Si tienes varios archivos, no te preocupes, siempre usará el último.

## 4. ¿Cómo ejecutar el proceso?

Ejecutar la herramienta es tan simple como hacer doble clic en un archivo.

1.  **Ve a la carpeta principal** del proyecto: `GestorDeValidaciones/`.
2.  Busca un archivo llamado `EJECUTAR_PROCESO.bat` (o similar).
3.  **Haz doble clic** sobre él.

Aparecerá una pantalla negra (la terminal) que te mostrará el progreso del proceso. Verás mensajes que indican qué etapa se está ejecutando, como "Preparación de datos SICS", "Integración Rimac", etc.

El proceso puede tardar unos segundos o minutos, dependiendo de la cantidad de datos. Cuando termine, la ventana se cerrará sola o te mostrará un mensaje de "Proceso finalizado".

## 5. Archivos de Salida: ¿Dónde están mis reportes?

Una vez que el proceso termina, tus reportes consolidados aparecerán en la carpeta `output`.

| Carpeta de Salida | Reporte Generado | Descripción |
| :--- | :--- | :--- |
| **`output/Rimac/`** | `Reporte-polizas_Rimac_FECHA.xlsx` | Contiene el cruce de datos de Rímac con SICS y SharePoint. |
| **`output/PacíficoIntegrado/`** | `Reporte-polizas_Pacifico_FECHA.xlsx` | Contiene el cruce de datos de Pacífico con SICS, SharePoint y el reporte de anulados. |

La `FECHA` en el nombre del archivo corresponde al día en que ejecutaste el proceso.

## 6. Interpretando los resultados

Los reportes generados contienen columnas adicionales que la herramienta calcula para ti. Aquí te explicamos las más importantes:

| Columna | ¿Qué significa? |
| :--- | :--- |
| **`SICS`** | Muestra la fecha de fin de vigencia de la póliza según SICS. Si dice **"No Encontrado"**, significa que esa póliza no se encontró en el reporte de SICS. |
| **`Tablero`** | Muestra el estado de la renovación según el archivo de SharePoint. Si dice **"No Encontrado"**, es que no está en ese archivo. |
| **`Responsable`** | Asigna automáticamente un responsable a la póliza basándose en reglas predefinidas (por ejemplo, por categoría o línea de negocio). |
| **`Observaciones`** | Contiene un comentario automático que te ayuda a entender la situación de la póliza. Por ejemplo, te puede indicar si la póliza está al día o si necesita revisión. |
| **`DentroRango`** | Es una de las columnas más útiles. Te dice **"Sí"** o **"No"** para indicarte si debes prestarle atención a esa póliza en este momento, según su fecha de vigencia y otras reglas. |
| **`Polizas Anulada`** (Solo en Pacífico) | Te indica si una póliza figura como anulada según el reporte específico de anulados. |

## 7. Solución a problemas comunes

| Problema | ¿Qué hacer? |
| :--- | :--- |
| **"No se pudo localizar el archivo de..."** | Este error significa que la herramienta no encontró el archivo de Excel que necesita. **Solución:** Asegúrate de que has colocado el archivo correcto en la carpeta `input` correspondiente (revisa la tabla de la sección 3). |
| **"Excel xlsx file; not supported"** | Este error suele ocurrir cuando un archivo que parece ser `.xls` en realidad tiene un formato interno diferente o está dañado. **Solución:** Abre el archivo `.xls` en Excel y guárdalo de nuevo, pero esta vez elige el formato **"Libro de Excel (.xlsx)"**. Luego, vuelve a colocarlo en su carpeta y ejecuta el proceso de nuevo. |
| **La ventana negra aparece y se cierra muy rápido.** | Esto puede significar que el proceso terminó muy rápido (¡lo cual es bueno!) o que hubo un error inicial. **Solución:** Revisa si los archivos de salida se generaron en la carpeta `output`. Si no están, verifica que todos los archivos de entrada estén en sus carpetas correctas. |

---

