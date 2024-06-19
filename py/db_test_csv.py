import cx_Oracle
import datetime
import logging
import csv
import sys
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

cx_Oracle.init_oracle_client(lib_dir=os.getenv('ORACLE_CLIENT_DIR'))

con_list = []
success_list = []
error_list = []

now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")
nowemail = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

logpathname = f"{os.getenv('LOGS_PATH')}DB_TEST_{now}.log"

#FORMATO Y CONFIGURACIÓN DE PINTADO DE LOGS
formatter = logging.Formatter("%(asctime)s %(message)s", "%Y-%m-%d %H:%M:%S ")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(logpathname, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#FUNCION DE CONEXION A BASE DE DATOS
def testDatabase(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT):
    logger.debug(f"[{DB_NAME}] - Intentando conectar a base de datos {DB_NAME}")
    try:
        with cx_Oracle.connect(
            user = DB_USER,
            password = DB_PASS,
            dsn=f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
            encoding='UTF-8', 
        ) as connection:
            if(connection):
                con_list.append([DB_NAME, True])
                connectmsg = f"[{DB_NAME}] - Se pudo conectar a la base de datos {DB_NAME}"
                logger.info(connectmsg)
    except Exception as ex:
        con_list.append([DB_NAME, False, ex, DB_HOST, DB_USER])
        errormsg = f"[{DB_NAME}] - No se pudo conectar a la base de datos: {DB_NAME}\n\t{ex}"
        logger.error(errormsg)
    
#FUNCIÓN DE LECTURA DE DATOS DE ARCHIVOS CSV
csvdatapath = f"{os.getenv('CSV_DATA_PATH')}databaseinfo.csv"

with open(csvdatapath, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        testDatabase(row[0], row[1], row[2], row[3], row[4])

#INFORME GENERAL DE BASE DE DATOS
resumee_log = f"RESUMEN DE PRUEBAS DE BASE DE DATOS:\n"

for elem in con_list:
    if (elem[1] == False):
        resumee_log += f"[Conexión a {elem[0]}] {elem[1]} ({elem[2]})\n"
    else:
        resumee_log += f"[Conexión a {elem[0]}] {elem[1]}\n"

logger.debug(resumee_log)

# --------- ENVÍO DE CORREO ---------

#Filtrado de Arreglo de conexión por errores
error_list = [arr for arr in con_list if arr[1] == False]

if len(error_list) > 0:
    urlAPI = os.getenv('ENVIOCORREO_API_URL')
    logger.info(f"[envioCorreo] Llamando a servicio envioCorreo: {urlAPI}")

    htmlrows = ""

    for elem in error_list:
        htmlrows += f"""<tr>
                <td style = "border: 1px solid black; text-align: center"><b>{elem[0]}</b></td>
                <td style = "border: 1px solid black; text-align: center; padding: 10px">{elem[4]}</td>
                <td style = "border: 1px solid black; text-align: center">{elem[3]}</td>
                <td style = "border: 1px solid black; padding: 10px">{elem[2]}</td>
            </tr>"""

    htmlmessage = f"""
        <div>
            <p>Se reportan las siguientes bases de datos con errores de conexión:</p>
        </div>
        <div style = "display: flex; justify-content: center; margin-top:20px">
            <Table style = "border: 1px solid black; padding-: 3px; border-collapse: collapse">
                <tr style = "border: 1px solid black; background-color: red">
                    <th style = "border: 1px solid black; color: white; min-width: 150px; text-align: center">Base de datos</th>
                    <th style = "border: 1px solid black; color: white; min-width: 50px; text-align: center">User</th>
                    <th style = "border: 1px solid black; color: white; min-width: 150px; text-align: center">Host</th>
                    <th style = "border: 1px solid black; color: white; text-wrap: wrap; text-align: center">Oracle Error</th>
                </tr>
                {htmlrows}
            </Table>
        </div>
        <div>
            <p><i>Fecha: {nowemail}<i>
            </p>
        </div>
    """
    requestData = {
        "auditRequest": {
            "idTransaccion": os.getenv('ENVIOCORREO_IDTRANSACCION'),
            "codigoAplicacion": os.getenv('ENVIOCORREO_CODIGOAPLICACION'),
            "ipAplicacion": os.getenv('ENVIOCORREO_IPAPLICACION'),
            "usrAplicacion": os.getenv('ENVIOCORREO_USRAPLICACION')
        },
        "remitente": os.getenv('ENVIOCORREO_REMITENTE'),
        "destinatario": os.getenv('ENVIOCORREO_DESTINATARIO'),
        "asunto": f"[ERROR EN BASE DE DATOS QA] - REPORTE {nowemail}",
        "mensaje": htmlmessage,
        "htmlFlag": "1"
    } 

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", urlAPI, headers=headers, data=json.dumps(requestData))
    responseHandler = response.json()

    # RESPONSE HANDLER
    if responseHandler["codigoRespuesta"] == "0":
        logger.debug(f"[envioCorreo] El correo se envió correctamente")
    else:
        logger.debug(f"[envioCorreo] Error al llamar al servicio envioCorreo: {response['mensajeRespuesta']}")
else:
    logger.info("[envioCorreo] Sin errores de conexión, no se enviará correo...") 

sys.exit()