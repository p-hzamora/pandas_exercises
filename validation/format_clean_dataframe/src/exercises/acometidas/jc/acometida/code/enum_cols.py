from enum import Enum

class FileCols(Enum):
    SOLICITUD_DE_PAGO = "Solicitud de Pago"
    EJECUTADO = "Ejecutado"
    REGISTRO_CONFORME = "Registro Conforme"
    FECHA_ULTIMO_DOC = "Fecha último doc "
    EMPRESA = "Empresa"
    OBSERVACIONES = "Observaciones"


class NewCols(Enum):
    SOLICITUD_DE_PAGO = "Solicitud\nPago"
    EJECUTADO = "Ejec."
    REGISTRO_CONFORME = "Registro"
    FECHA_ULTIMO_DOC = "Última Fecha"
    EMPRESA = "Empresa"
    OBSERVACIONES = "Observaciones"
