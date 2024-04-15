import cx_Oracle
import datetime
import logging
import csv

con_list = []
now = datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")

logpathname = f"C:\env\DB_TEST\logs\DB_TEST_{now}.log"

#FORMATO Y CONFIGURACIÓN DE PINTADO DE LOGS
formatter = logging.Formatter("[%(asctime)s]%(message)s", "%Y-%m-%d %H.%M.%S")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(logpathname, mode='w')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

#FUNCION DE CONEXION A BASE DE DATOS
def testDatabase(DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT):
    logger.debug(f"INTENTANDO CONEXIÓN A BASE DE DATOS: {DB_NAME}")
    try:
        with cx_Oracle.connect(
            user = DB_USER,
            password = DB_PASS,
            dsn=f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
            encoding='UTF-8', 
        ) as connection:
            if(connection):
                con_list.append([DB_NAME, True])
                connectmsg = f"SE PUDO CONECTAR CORRECTAMENTE A LA BASE DE DATOS: {DB_NAME}"
                logger.info(connectmsg)
    except Exception as ex:
        con_list.append([DB_NAME, False, ex])
        errormsg = f"NO SE PUDO CONECTAR A LA BASE DE DATOS: {DB_NAME}\n\t{ex}"
        logger.error(errormsg)
    
#FUNCIÓN DE LECTURA DE DATOS DE CSV
csvdatapath = 'C:\env\DB_TEST\data\databaseinfo.csv'
with open(csvdatapath, newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        testDatabase(row[0], row[1], row[2], row[3], row[4])

#INFORME GENERAL DE BASE DE DATOS
resumee_log = f"RESUMEN DE PRUEBAS DE BASE DE DATOS:\n"

for elem in con_list:
    if (len(elem) == 3):
        resumee_log += f"\t[Conexión a {elem[0]}] {elem[1]} ({elem[2]})\n"
    else:
        resumee_log += f"\t[Conexión a {elem[0]}] {elem[1]}\n"

logger.debug(resumee_log)