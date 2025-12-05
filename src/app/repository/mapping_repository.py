MAPEO = {
    "Tablero_Sharepoint":[
        "NIT",
        "CLIENTE",
        "ASEG.",
        "RIESGO",
        "PRODUCTO",
        "NRO_POLIZA",
        "Pol origen",
        "Placa",
        "Fecha Fin vigencia",
        "Clasificación",
        "Responsable",
        "MES FV",
        "FECHA ENTREGA PROP. RENOVACION",
        "DIAS DE ENTREGA",
        "RESULTADO DE ENTREGA",
        "STATUS RENOVACION", # Se escoge para procesamiento
        "MOTIVO",
        "ASEGURADORA",
        "RENOVADA",
        "POLIZANUEVA",
        "OBSERVACIONES",
        "Cumple ANS",
        "Detalle de no cumplimento de ANS",
        "F. Venc. SICS", # Se escoge para procesamiento
        "Pólizafinal", # Se escoge para procesamiento
        "Pacifico", # campo nuevo Pacífico creado a partir de NRO_POLIZA
        "Rimac" # campo nuevo Rimac creado a partir de NRO_POLIZA
    ],
    "Tablero_SICS":[
        "Cod Cia",
        "Aseguradora",
        "Cod Ramo",
        "Ramo / Producto",
        "Póliza",
        "Pacifico", # campo nuevo Pacífico creado a partir de Póliza
        "Rimac", # campo nuevo Rimac creado a partir de Póliza
        "Orden",
        "Nit / CC",
        "Nombre / Razón Social Tomador",
        "Nombre / Razón Social Asegurado",
        "Nombre / Razon Social Beneficiario",
        "Vig Desde Póliza",
        "Vig Hasta Póliza",
        "Fin Vig", # Se crea a partir de Vig Hasta Póliza
        "No. Certificado",
        "Vlr Prima",
        "Fecha Inclusión",
        "Fecha Exclusión",
        "Placa",
        "Chasis",
        "Unidad de Negocio",
        "Documento Tomador"
    ],
    "Tablero_RIMAC": [
        "RESPONSABLE DE PAGO",
        "NRO. POLIZA",
        "CATEGORÍA",
        "DOCUMENTO",
        "MEDIO DE PAGO",
        "MONTO",
        "CUOTA",
        "VENCIMIENTO",
        "ESTADO"
    ],
    "Tablero_Integración_rimac": [
        "RESPONSABLE DE PAGO",
        "NRO. POLIZA",
        "SICS",
        "Tablero",
        "Observaciones",
        "Responsable",
        "CATEGORÍA",
        "VENCIMIENTO",
        "Obs",
        "SICS"
    ],
    "tablero_PACIFICO":[
        "Contratante",
        "Tipo de Documento",
        "Nro de Documento",
        "Linea de Negocio",
        "Producto",
        "Nro de Poliza/Contrato",
        "Renovacion",
        "Inicio de Vigencia",
        "Fin de Vigencia",
        "Prima Bruta Dolares",
        "Prima Bruta Soles",
        "Estado",
        "Situacion"
    ],
    "tablero_integracion_pacifico":[
        "Contratante",
        "Nro de Documento",
        "Linea de Negocio",
        "Producto",
        "Nro de Poliza/Contrato",
        "SICS",
        "Tablero",
        "Observaciones",
        "Responsable",
        "Fin de Vigencia",
        "Situacion",
        "OBS",
        "Polizas Anulada",
        "Cedidos"
    ],
    "Responsables": {
        "Briyan": [
            "SALUD RED PREFERENTE",
            "SALUD RED PREFERENTE F F V V",
            "SALUD RED MEDICA F F V V",
            "SALUD DE ORO F F V V",
            "SALUD FLEXIBLE",
            "FULLSALUD",
            "ONCO.INTEGRAL INDIVIDUAL BROKERS",
            "EPS",
            "SALUD PREFERENCIAL",
            "FULL SALUD F F V V",
            "SALUD RED MÉDICA",
            "FULLSALUD",
            "SALUD DE ORO",
            "SALUD RED MEDICA HOSPITALARIA",
            "ONCO. INTEGRAL INDIVIDUAL BROKERS",
            "ASISTENCIA MEDICA COLECTIVAS"
        ],
        "Cesar": [
            "WEB VEHICULOS",
            "DOMICILIARIO RIMAC (EX CASASEGURA)",
            "SOAT"
        ],
        "Jesus": [
            "S.C.T.R. - PENSION",
            "VIDA LEY D.L. 688",
            "VIDALEYRE",
            "S.C.T.R. - SALUD",
            "VIDA GRUPO",
            "FORMACION LABORAL",
            "VIDA LEY 2DA CAPA",
            "ONCOLÓGICO RIMAC",
            "ACCIDENTES SEGURO VIDA B"
        ],
        "Thalia":[
            "CASCOS",
            "TREC",
            "NEGOCIO SEGURO",
            "RESPONSABILIDAD CIVIL",
            "AVIACION",
            "MULTI RIESGO",
            "3D",
            "ROBO",
            "TRANSPORTE FLOTANTE"
        ]
    },
    "Responsables_Pacifico":[
        {
         "Linea": "EPS Regular",
         "Producto": "EPS Regular",
         "Responsable": "Briyan"
         },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Medic Vida Internacional",
            "Responsable": "Briyan"
        },
        {
            "Linea": "EPS Individual",
            "Producto": "EPS Individual",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Seguro Oncologico Nacional",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Seguro Oncologico Internacional",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Multisalud",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Medic Vida Nacional",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Medic Vida",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Seguro de Enfermedades Graves Internacional",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto": "Seguro Oncologico Colectivo Empresa",
            "Responsable": "Briyan",
        },
        {
           "Linea": "Asistencia Medica",
            "Producto": "Seguro de Salud Red Preferente",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "Premium Life Max",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "Total Life Protection",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "Term 65 Nivelado",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "University Life 10",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "Vida Individual",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "University Life 17",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "Devolución Total 15",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Vida Individual",
            "Producto": "SEG. DE VIDA DEVOLUCIÓN TOTAL 25 SOLES 125%",
            "Responsable": "Briyan"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Seguro de Hogar",
            "Responsable": "Cesar"
        },
        {
            "Linea": "Autos",
            "Producto":"Auto Modular",
            "Responsable": "Cesar"
        },
        {
            "Linea": "Autos",
            "Producto":"Auto a Medida",
            "Responsable": "Cesar"
        },
        {
            "Linea": "Autos",
            "Producto":"Seguro de Autos Empresarial a la Medida",
            "Responsable": "Cesar"
        },
        {
            "Linea": "SOAT",
            "Producto":"SOAT Tradicional",
            "Responsable": "Cesar"
        },
        {
            "Linea": "Vida Ley",
            "Producto":"Vida Ley Trabajadores",
            "Responsable": "Jesus"
        },
        {
            "Linea": "SCTR Salud",
            "Producto":"SCTR Salud",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Vida Ley",
            "Producto":"Vida Ley Empleados",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Vida Ley",
            "Producto":"Vida Ley Obreros",
            "Responsable": "Jesus"
        },
        {
            "Linea": "SCTR Pension",
            "Producto":"SCTR Pensión",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Vida Grupo",
            "Producto":"Complementario a Vida Ley",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto":"Seguro de Salud Colectivo Practicantes",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Asistencia Medica",
            "Producto":"Seguro de Salud Practicantes",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Vida Ley",
            "Producto":"Vida Ley Empleados",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Accidentes Colectivos - Empleados (Suma fija)",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Accidentes Colectivos - Aforo",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Accidentes Individuales",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Accidentes Colectivos - Eventos",
            "Responsable": "Jesus"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"Transportes Carga Abierta",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Lineas Personales",
            "Producto":"Multiriesgo Negocio Empresarial PYME",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"SEGURO PATRIMONIAL",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"Transportes - Pólizas Individuales",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"Cascos No Pesqueros",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"CAR",
            "Responsable": "Thalia"
        },
        {
            "Linea": "Riesgos Generales",
            "Producto":"SEGURO PATRIMONIAL",
            "Responsable": "Thalia"
        }
    ],
    "Comentario": {
         1: "No está cargado en el SICS-Tablero",
         2: "Actualizar la vigencia en el SICS",
         6: "Revisar renovación"
    },
    "Comentario_Pacifico": {
        1: "No está cargado en el SICS-Tablero",
        2: "Actualizar la vigencia en el SICS",
        3: "Por renovar en Pacifico"
    },
    "Anulados": [
        "Contratante",
        "Nro de Documento",
        "Producto",
        "Nro de Poliza/Contrato",
        "Tablero	Observaciones",
        "Fin de Vigencia",
        "Situacion"
    ]

}
