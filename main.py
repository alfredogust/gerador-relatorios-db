"""
Classe App, responsável por gerir a interface e a conexão com o banco de dados.

Fornece métodos para conectar ao banco de dados, escoher diretórios,
processar dados e encerrar a conexão.
"""

import logging
import os
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from logs.logger import configurar_logger
#from src.config import dir_destino
from src.processamento_dados.data_processor import DataProcessor
from src.ui import UiMainWindow


class App(QMainWindow):
    """Classe principal do aplicativo."""

    def __init__(self) -> None:
        """Inicializa a classe App."""
        super().__init__()

        self.ui = UiMainWindow()
        self.ui.setup_ui(self)
        self.data_processor = None
        self.dir_destino = ""
        print(self.dir_destino)

        configurar_logger(arquivo_log="data_processor.log")
        self.configurar_botoes()
        self.ui.combo_box_banco_dados.addItems(
            ["","EQUATORIAL_SUL", "EQUATORIAL_GOIAS"]
            )
        self.ui.combo_box_banco_dados.currentIndexChanged.connect(self.conectar)

    def configurar_botoes(self):
        """Configura os botões da interface."""
        #self.ui.push_button_conectar.clicked.connect(self.conectar)
        self.ui.push_button_extrair.clicked.connect(self.fluxo_dos_dados)
        #self.ui.push_button_cancelar.clicked.connect(self.encerrar_conexao)
        self.ui.tool_button.clicked.connect(self.selecionar_diretorio)

    def conectar(self):
        """Método para conectar ao banco de dados selecionado."""
        combo_box_banco_dados = self.ui.combo_box_banco_dados

        if combo_box_banco_dados is not None:
            banco_selecionado = combo_box_banco_dados.currentText()

            if banco_selecionado == "EQUATORIAL_SUL":
                projeto_combo_box = self.ui.combo_box_projeto
                projeto_combo_box.clear()
                projeto_combo_box.addItems(["", "BAG", "CAM", "MRE"])
                print(projeto_combo_box)
                '''projeto_combo_box.currentIndexChanged.connect(
                    self.fluxo_dos_dados
                    )'''

            if banco_selecionado == "EQUATORIAL_GOIAS":
                projeto_combo_box = self.ui.combo_box_projeto
                projeto_combo_box.clear()
                projeto_combo_box.addItems(["", "FIR", "TUR"])
                '''projeto_combo_box.currentIndexChanged.connect(
                    self.fluxo_dos_dados
                    )'''
                
            if self.data_processor is not None:
                self.encerrar_conexao()

            try:
                dir_banco = os.path.join(self.dir_destino, banco_selecionado)
                os.makedirs(dir_banco, exist_ok=True)

                self.data_processor = DataProcessor(
                    banco_selecionado, dir_banco, self.dir_destino
                )
                self.data_processor.get_db_connection()
                logging.info("Conexão com o banco de dados bem-sucedida!")

                self.ui.label_status_conexao_retorno.setText("Conectado!")

            except ConnectionError as e:
                logging.error("Erro ao conectar ao banco de dados: %s", e)
                self.ui.label_status_conexao_retorno.setText(
                    f"Erro de Conexão: {e}"
                )
            except FileNotFoundError as e:
                logging.error(
                    "Erro ao encontrar o arquivo do banco de dados: %s", e
                )
                self.ui.label_status_conexao_retorno.setText(
                    f"Erro de Arquivo: {e}"
                )
            except Exception as e:
                logging.error(
                    "Erro inesperado ao conectar ao banco de dados: %s", e
                )
                self.ui.label_status_conexao_retorno.setText(
                    f"Erro Inesperado: {e}"
                )
            else:
                print(
                    "Erro: Impossível encontrar objeto 'combo_box_banco_dados'"
                )

    def selecionar_diretorio(self):
        """Abre uma caixa de diálogo para o usuário escolher um diretório."""
        diretorio = QFileDialog.getExistingDirectory(
            self, "Selecione um diretório"
        )

        if diretorio:
            self.ui.line_edit_diretorio.setText(diretorio)
            self.dir_destino = diretorio

    def fluxo_dos_dados(self):
        """Processa os dados do banco de dados."""
        if self.data_processor is None:
            return

        projeto = self.ui.combo_box_projeto.currentText()
        if projeto == "":
            self.ui.label_status_conexao_retorno.setText(
                "Selecione um projeto!"
            )
            return

        dir_projeto = os.path.join(self.data_processor.dir_banco, projeto)
        os.makedirs(dir_projeto, exist_ok=True)

        self.data_processor.dir_destino = dir_projeto

        dataframe_original = self.data_processor.extrair_dados(projeto=projeto)

        if dataframe_original is not None:
            self.data_processor.processar_cadastros(dataframe_original)

            self.exibir_mensagem_sucesso()

    def exibir_mensagem_sucesso(self):
        '''Exibe a mensagem de sucesso na interface.'''
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Sucesso")
        msg_box.setText("Dados extraídos e salvos com sucesso!")
        msg_box.setInformativeText(f"Arquivos salvos em: {self.data_processor.dir_destino}")
        msg_box.exec_()

        if msg_box.clickedButton() == msg_box.button(QMessageBox.Ok):
            self.encerrar_conexao()
            self.ui.label_status_conexao_retorno.setText("Conexão encerrada.")


    def encerrar_conexao(self):
        """Fecha conexão com o banco de dados."""
        if self.data_processor is not None:
            self.data_processor.close_connection()
            self.data_processor = None
            self.ui.label_status_conexao_retorno.setText(
                "Conexão encerrada!"
            )

            self.ui.combo_box_projeto.setCurrentIndex(0)
            self.ui.combo_box_banco_dados.setCurrentIndex(0)
        else:
            self.ui.label_status_conexao_retorno.setText(
                "Nenhuma conexão ativa."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())
