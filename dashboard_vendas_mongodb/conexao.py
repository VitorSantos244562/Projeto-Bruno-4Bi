"""Conexão com o MongoDB Atlas usando as configurações do arquivo .env."""
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError


# Lê o arquivo .env que fica ao lado deste arquivo Python.
load_dotenv(Path(__file__).with_name('.env'))


def conectar():
    """Confere a conexão com ping e retorna o cliente e o banco didático."""
    uri = os.getenv('MONGO_URI', 'mongodb+srv://root:Veeronica@cluster0.jifco89.mongodb.net/')
    if not uri or '<' in uri or '>' in uri:
        raise ValueError(
            'Configure MONGO_URI no arquivo .env com a URI real do MongoDB Atlas.'
        )

    cliente = MongoClient(uri, serverSelectionTimeoutMS=8000)
    try:
        cliente.admin.command('ping')  # Envia um comando real ao servidor.
    except PyMongoError as erro:
        cliente.close()
        raise ConnectionError(
            'Não foi possível acessar o MongoDB. Verifique a URI, '
            'o usuário/senha e o IP autorizado no Atlas.'
        ) from erro

    banco = cliente['laboratorio_python']
    return cliente, banco


if __name__ == '__main__':
    try:
        cliente, banco = conectar()
        print('Ping realizado com sucesso!')
        print('Conectado ao banco:', banco.name)
        cliente.close()
    except (ConnectionError, ValueError) as erro:
        print('ERRO:', erro)
        raise SystemExit(1)
