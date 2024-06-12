import logging

def configurar_logger(arquivo_log='data_processor.log', nivel_log=logging.INFO):
    """Configura o logging para o aplicativo."""
    logging.basicConfig(filename=arquivo_log, level=nivel_log,
                        format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')