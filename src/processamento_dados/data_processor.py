"""
Este módulo contém a classe DataProcessor, responsável por processar dados de cadastros.

O DataProcessor conecta-se a um banco de dados, extrai dados, agrupa-os por cadastrador
e data, e salva os resultados em arquivos Excel. O módulo também define classes para
processar diferentes tipos de cadastros, como PG, IP e CONSUMIDOR.
"""
import logging
import os
import pandas as pd
import psycopg2
import psycopg2.extras
from src.config import db_config

# pylint: disable=too-few-public-methods

class DataProcessor:
    """
    Classe que processa dados de um arquivo Excel, insere no banco de dados e realiza agrupamentos.

    Esta classe fornece métodos para conectar ao banco de dados, extrair dados,
    agrupar dados por cadastrador e data, e salvar os resultados em arquivos Excel.
    """


    def __init__(self, banco_selecionado, dir_banco, dir_destino):
        """Inicializa a classe com o caminho do arquivo excel e configurações do banco de dados."""
        self.banco_selecionado = banco_selecionado
        self.dir_banco = dir_banco
        self.dir_destino = dir_destino
        
    def get_db_connection(self):
        """Obtém uma conexão com o banco de dados."""
        try:
            db_config["database"] = self.banco_selecionado
            self.conexao = psycopg2.connect(**db_config)
            logging.info("Conexão com o banco de dados bem-sucedida!")
            print("Conexão com o banco de dados bem-sucedida!")

        except Exception as e:
            print(e)
            logging.error("Erro ao conectar ao banco de dados: %s", e)
            raise ConnectionError("Falha na conexão com o banco de dados") from e

    def extrair_dados(self, projeto):
        """
        Executa uma consulta SQL no banco de dados e retorna um DataFrame Pandas.

        Args:
            projeto (str): O nome do projeto para o qual os dados serão extraídos.

        Returns:
            pd.DataFrame: DataFrame contendo os resultados da consulta SQL.

        Raises:
            ConnectionError: Se a conexão com o banco de dados não estiver estabelecida.
            Exception: Se houver erro ao executar a consulta SQL.
        """
        if self.conexao is None:
            raise ConnectionError("Conexão com o banco de dados não estabelecida")

        query = f'SELECT * FROM "{projeto}"."pg";'

        try:
            cursor = self.conexao.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            dados = cursor.fetchall()
            cursor.close()

            dataframe = pd.DataFrame(dados)
            print(f"DataFrame extraído com sucesso: {dataframe.head()}")
            return dataframe

        except Exception as e:
            logging.error("Erro ao executar a consulta SQL: %s", e)
            raise

    def processar_cadastros(self, dataframe_original):
        """Processa os dados para cada tipo de cadastro."""
        tipos_de_cadastro = {
            "PG": ProcessadorPG,
            "IP": ProcessadorIP,
            "CONSUMIDOR": ProcessadorConsumidor,
            # 'USO MUTUO': ProcessadorUsoMutuo,  # Adicione métodos para outros tipos de cadastro
            # 'ESTRUTURA': ProcessadorEstrutura, # Adicione métodos para outros tipos de cadastro
        }

        for tipo_cadastro, processador in tipos_de_cadastro.items():
            print(f"Processando tipo de cadastro: {tipo_cadastro}")
            processador(dataframe_original, self.dir_destino, self).processar()

    def salvar_dataframe(self, df, nome_arquivo="pg_cadastro_tratado"):
        """Salva um DataFrame em um novo arquivo Excel"""
        print(f"Chamando salvar_dataframe com o DF: {type(df)}")
        extensao_arquivo = ".xlsx"
        novo_nome_arquivo = os.path.join(
            self.dir_destino, f"{nome_arquivo}{extensao_arquivo}"
        )

        if os.path.exists(novo_nome_arquivo):
            contador = 1
            while os.path.exists(
                os.path.join(
                    self.dir_destino, f"{nome_arquivo}_{contador}{extensao_arquivo}"
                )
            ):
                contador += 1
            novo_nome_arquivo = os.path.join(
                self.dir_destino, f"{nome_arquivo}_{contador}{extensao_arquivo}"
            )

        df.to_excel(novo_nome_arquivo, index=False)
        logging.info("DataFrame salvo em: %s", novo_nome_arquivo)

    def close_connection(self):
        """Fecha a conexão com o banco de dados."""
        if self.conexao:
            self.conexao.close()
            self.conexao = None
            logging.info("Conexão com o banco de dados fechada.")
            print("Conexão com o banco de dados fechada.")


class Agrupador:
    """
    Classe para agrupar dados por cadastrador e data.

    Args:
        dataframe (pd.DataFrame): DataFrame contendo os dados a serem agrupados.
        coluna_cadastrador (str): Nome da coluna do DataFrame com os cadastradores.
        coluna_data (str): Nome da coluna do DataFrame com as datas.

    Methods:
        agrupar(): Agrupa os dados por cadastrador e data.

    Returns:
        pd.DataFrame: DataFrame com o número de ocorrências por cadastrador e data.
    """
    def __init__(self, dataframe, coluna_cadastrador, coluna_data):
        self.dataframe = dataframe
        self.coluna_cadastrador = coluna_cadastrador
        self.coluna_data = coluna_data

    def agrupar(self):
        """
        Agrupa os dados do DataFrame por cadastrador e data.

        Este método converte a coluna de data para o formato datetime,
        ordena o DataFrame por data e depois realiza a contagem de 
        ocorrências para cada combinção de cadastrador e data.

        Returns:
            pd.DataFrame: DataFrame contendo os dados agrupados.
        """
        self.dataframe[self.coluna_data] = pd.to_datetime(
            self.dataframe[self.coluna_data],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )
        self.dataframe = self.dataframe.sort_values(by=self.coluna_data)
        grupo = (
            self.dataframe.groupby(
                [self.coluna_cadastrador, self.dataframe[self.coluna_data].dt.date]
            )
            .size()
            .reset_index(name="Produção")
        )
        grupo = grupo.sort_values(by=[self.coluna_data])

        return grupo


class ProcessadorPG:
    """
    Classe para processar cadastros do tipo PG.

    Args:
        dataframe (pd.DataFrame): DataFrame contendo os dados a serem processados.
        dir_destino (str): Diretório de destino para os arquivos de saída.
        data_processor (DataProcessor): Instância do DataProcessor para acesso a métodos auxiliares.

    Methods:
        processar(): Processa os cadastros PG, salvando os resultados em arquivos Excel.

    Returns:
        None
    """
    def __init__(self, dataframe, dir_destino, data_processor):
        self.dataframe = dataframe
        self.dir_destino = dir_destino
        self.data_processor = data_processor

    def processar(self):
        """
        Processa os dados relacionados a 'PG'.

        Salva os intervalos de tempo e agrupa os campos relevantes para 'PG',
        em seguida, salva os dados processados em arquivos Excel.
        """
        print("Salvando intervalos de tempo do cadastrador para PG...")
        self.intervalos_tempo_cadastrador_pg(
            tipo_cadastro="PG",
            dataframe=self.dataframe,
            nome_arquivo_saida="Media_PG",
            dir_destino=self.dir_destino,
        )

        print("Agrupando campos relevantes para PG...")
        agrupador = Agrupador(
            self.dataframe, "cadastrista_pg", "data_cadastro_pg_escritorio"
        )
        agrupa_campos_pg = agrupador.agrupar()

        print("Processando cadastros PG...")
        self.data_processor.salvar_dataframe(
            df=agrupa_campos_pg, nome_arquivo="Producao_PG"
        )

    def intervalos_tempo_cadastrador_pg(
        self, tipo_cadastro, dataframe, nome_arquivo_saida, dir_destino
    ):
        """Recebendo dataFrame sem tratamento"""
        if tipo_cadastro == "PG":

            coluna_cadastrista = f"cadastrista_{tipo_cadastro.lower()}"
            cadastristas = dataframe[coluna_cadastrista].unique()

            writer = pd.ExcelWriter(
                os.path.join(dir_destino, f"{nome_arquivo_saida}.xlsx"),
                engine="xlsxwriter",
            )

            for colaborador in cadastristas:
                df_entidade = dataframe[dataframe[coluna_cadastrista] == colaborador]
                df = df_entidade[
                    ["cadastrista_pg", "data_cadastro_pg_escritorio"]
                ].copy()
                df["data_cadastro_pg_escritorio"] = pd.to_datetime(
                    df["data_cadastro_pg_escritorio"],
                    format="%d/%m/%Y %H:%M:%S",
                    errors="coerce",
                )
                df = df.sort_values(by="data_cadastro_pg_escritorio")
                df["Intervalo_min"] = (
                    df["data_cadastro_pg_escritorio"].shift(-1)
                    - df["data_cadastro_pg_escritorio"]
                ).dt.total_seconds() / 60
                df["Intervalo_min"] = df["Intervalo_min"].fillna(0)
                df["Intervalo_min"] = df["Intervalo_min"].apply(
                    lambda x: f"{int(x // 60):02}:{int(x % 60):02}:{int((x % 1) * 60):02}"
                )
                df.to_excel(writer, sheet_name=str(colaborador), index=False)

            writer.close()
            print(f"Arquivo Excel '{nome_arquivo_saida}' criado com sucesso!")


class ProcessadorIP:
    """
    Classe para processar cadastros do tipo IP.

    Args:
        dataframe (pd.DataFrame): DataFrame contendo os dados a serem processados.
        dir_destino (str): Diretório de destino para os arquivos de saída.
        data_processor (DataProcessor): Instância do DataProcessor para acesso a métodos auxiliares.

    Methods:
        processar(): Processa os cadastros IP, salvando os resultados em arquivos Excel.

    Returns:
        None
    """
    def __init__(self, dataframe, dir_destino, data_processor):
        self.dataframe = dataframe
        self.dir_destino = dir_destino
        self.data_processor = data_processor

    def processar(self):
        """Processa os dados de IP."""
        print("Agrupando campos relevantes para IP...")
        agrupador = Agrupador(self.dataframe, "cadastrista_ip", "data_cadastro_ip")
        agrupa_campos_ip = agrupador.agrupar()
        print("Processando cadastros IP...")
        self.data_processor.salvar_dataframe(
            agrupa_campos_ip, nome_arquivo="Producao_IP"
        )


class ProcessadorConsumidor:
    """
    Classe para processar cadastros do tipo CONSUMIDOR.

    Args:
        dataframe (pd.DataFrame): DataFrame contendo os dados a serem processados.
        dir_destino (str): Diretório de destino para os arquivos de saída.
        data_processor (DataProcessor): Instância do DataProcessor para acesso a métodos auxiliares.

    Methods:
        processar(): Processa os cadastros CONSUMIDOR, salvando os resultados em arquivos Excel.

    Returns:
        None
    """
    def __init__(self, dataframe, dir_destino, data_processor):
        self.dataframe = dataframe
        self.dir_destino = dir_destino
        self.data_processor = data_processor

    def processar(self):
        """
        Agrupa os campos relevantes para o tipo de cadastro CONSUMIDOR e processa os cadastros.

        Este método usa um objeto Agrupador para os dados do DataFrame por cadastrador e data, e
        em seguida processa os cadastros CONSUMIDOR.Dados agrupados são salvos em um arquivo Excel.

        """
        print("Agrupando campos relevantes para CONSUMIDOR...")
        agrupador = Agrupador(
            self.dataframe, "cadastrista_consumidor", "data_cadastro_consumidor"
        )
        agrupa_campos_consumidor = agrupador.agrupar()
        print("Processando cadastros CONSUMIDOR...")
        self.data_processor.salvar_dataframe(
            agrupa_campos_consumidor, nome_arquivo="Producao_CONSUMIDOR"
        )
