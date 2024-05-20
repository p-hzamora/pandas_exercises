class Cols:
    nombre = "Nombre Acometida"
    solicitud = "Solicitud de Pago"
    ejecutado = "Ejecutado"
    registro = "Registro Conforme"
    fecha = "Fecha último doc"
    empresa = "Empresa"
    observaciones = "Observaciones"

    @classmethod
    def get_all_cols(cls) -> list[str]:
        dicc_to_translate: dict[Cols, str] = {
            cls.solicitud: "Solicitud\nPago",
            cls.ejecutado: "Ejec.",
            cls.registro: "Registro",
            cls.fecha: "Última Fecha",
            cls.empresa: "Empresa",
            cls.observaciones: "Observaciones",
        }
        
        translated_list:list[str] = []
        for x in Cols.__dict__.keys():
            att = getattr(cls,x)
            if not x.startswith("__") and not callable(att):
                translated_list.append(dicc_to_translate.get(att, x))
            
        return translated_list