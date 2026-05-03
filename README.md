# Análisis de Nacidos Vivos en el Perú

Este repositorio contiene los datos del "Registro de Nacidos Vivos en el Perú".

## Contenido
- `CNV_MINSA_CORTE_30112025.zip`: Base de datos comprimida de los registros de nacidos vivos (aprox. 830 MB descomprimido).
- `RENIPRESS.csv`: Datos de instituciones prestadoras de servicios de salud.
- `Lista_Ubigeos_INEI.csv`: Códigos de Ubigeo del INEI.
- `Diccionario de Datos - CNV.pdf`: Diccionario de variables de la base de datos.

## Cómo usar en Google Colab

Puedes descargar y extraer los datos directamente en un cuaderno de Google Colab ejecutando las siguientes celdas:

```python
# Clonar el repositorio
!git clone https://github.com/ArnoldZamoratec/analisis-nacidos-vivos-peru.git

# Cambiar al directorio
%cd analisis-nacidos-vivos-peru

# Descomprimir la base de datos principal
!unzip CNV_MINSA_CORTE_30112025.zip
```

Luego, puedes cargar los datos con `pandas`:

```python
import pandas as pd

# Cargar los datos. Nota: El separador es punto y coma (;)
df_nacidos = pd.read_csv('CNV_MINSA_CORTE_30112025.csv', sep=';', encoding='latin-1')

# Ver las primeras filas
df_nacidos.head()
```
