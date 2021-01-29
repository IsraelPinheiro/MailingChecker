import os, argparse, re
import pandas as pd
from datetime import datetime
from time import perf_counter

parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", help="Input Files location", type=str, default=r"./Input")
parser.add_argument("--output", "-o", help="Output Files location", type=str, default=r"./Output")
parser.add_argument("--verbose", "-v", help="If the program should run in verbose mode", type=bool, default=True)
parser.add_argument("--log", "-l", help="Either if logs should be enabled or not", type=bool, default=True)
args = parser.parse_args()

INPUT_PATH = args.input
OUTPUT_PATH = args.output
VERBOSE = args.verbose
LOG = args.log
LOGS_PATH = "./Logs"

class MailingChecker():
    INPUT_FILES = None

    def __init__(self):
        self.initialise()
        self.processFiles()

    def initialise(self):
        if not os.path.exists(LOGS_PATH):
            os.makedirs(LOGS_PATH, exist_ok=True)
            self.log("The logs folder doesn't exists, creating...")
        if not os.path.exists(INPUT_PATH):
            self.log("The specified input path doesn't exists, creating...")
            os.makedirs(INPUT_PATH, exist_ok=True)
        if not os.path.exists(OUTPUT_PATH):
            self.log("The specified output path doesn't exists, creating...")
            os.makedirs(OUTPUT_PATH, exist_ok=True)
        #Initialize input files list
        self.INPUT_FILES = [file for file in os.listdir(INPUT_PATH) if os.path.isfile(os.path.join(INPUT_PATH, file))]

    def log(self, message):
        if LOG or VERBOSE:
            now = datetime.now()
            LOG_FILE = f"{LOGS_PATH}/{now.strftime('%Y-%m-%d')}.log"
            message = f"{now.strftime('%d/%m/%Y - %H:%M:%S.%f')} - {message}"
            if LOG:
                with open(LOG_FILE, "a+", encoding="utf-8") as f:
                    f.write(f"{message}\n")
            if VERBOSE:
                print(message)

    def processFiles(self):
        for file in self.INPUT_FILES:
            self.processFile(file)

    def processFile(self, file:str):
        self.log(f"Processing file '{file}'")
        headers = ["ID_MAILING","ID_TITULO","NOME","CONTRATO","TIPO_DE_PESSOA","CPF","UF","CIDADE","SITUACAO_DO_CONTRATO","SALDO","VALOR_PARCELA","VALOR_EM_ATRASO","VALOR_DE_RISCO","QUANTIDADE_DE_PAGAMENTOS","PRODUTO","SEXO_DO_CLIENTE","DATA_ULTIMO_PAGAMENTO","DATA_DE_DISTRIBUICAO","DATA_DA_ULTIMA_DISTRIBUICAO","DIAS_DE_ATRASO","DIAS_SEM_CPC","DIAS_SEM_ATENDIMENTO","DIAS_SEM_ACIONAMENTO","CORINGA_1","CORINGA_2","CORINGA_3","CORINGA_4","CORINGA_5","CORINGA_6","CORINGA_7","CORINGA_8","TELEFONE_01","CAMPO VAZIO_01","TELEFONE_02","CAMPO VAZIO_02","TELEFONE_03","CAMPO VAZIO_03","TELEFONE_04","CAMPO VAZIO_04","TELEFONE_05","CAMPO VAZIO_05","TELEFONE_06","CAMPO VAZIO_06","TELEFONE_07","CAMPO VAZIO_07","TELEFONE_08","CAMPO VAZIO_08","TELEFONE_09","CAMPO VAZIO_09","CAMPO VAZIO_10","CAMPO VAZIO_11","CAMPO VAZIO_12","CAMPO VAZIO_13"]
        df = pd.read_csv(f"{INPUT_PATH}/{file}", sep=';', names=headers,encoding="ISO-8859-1", dtype=str) #Loads the CSV file into a dataframe
        df.fillna('', inplace=True) #Replace NaN with a empty string
    
        for _, row in df.iterrows():
            row = self.add9(row)
            row = self.removeDuplicates(row)

        self.log(f"File '{file}' processed")
        df.to_csv(f"{OUTPUT_PATH}/{file}", index=False, header=False, sep=';', encoding="utf-8-sig")
        self.log(f"Processed '{file}' saved to {OUTPUT_PATH}")

    def add9(self, row):
        for i in range(1,10):
            if row[f"TELEFONE_0{i}"] != "" and len(row[f"TELEFONE_0{i}"])==10 and (row[f"TELEFONE_0{i}"][2] == "9" or row[f"TELEFONE_0{i}"][2] == "8"):
                row[f"TELEFONE_0{i}"] = row[f"TELEFONE_0{i}"][:2] + "9" + row[f"TELEFONE_0{i}"][-8:]
        return row
                
    def removeDuplicates(self, row):
        phones = set()
        for i in range(1,10):
            if self.isPhone(row[f"TELEFONE_0{i}"]):
                phones.add(row[f"TELEFONE_0{i}"])
                row[f"TELEFONE_0{i}"] = ""

        i=1
        for phone in phones:
            row[f"TELEFONE_0{i}"] = phone
            i+=1
        return row

    def isPhone(self, phone):
        regex = "^[1-9]{2}(?:[2-8]|9[1-9])[0-9]{7}$"
        if re.match(regex, phone):
            return True
        else:
            return False

if __name__ == '__main__':
    start_time = perf_counter()
    mc = MailingChecker()
    print(f"{len(mc.INPUT_FILES)} file(s) processed in {round(perf_counter()- start_time, 2)} seconds")