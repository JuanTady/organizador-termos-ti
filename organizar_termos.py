"""
Organizador de Termos de Responsabilidade de Ativos de TI.

Este script automatiza a separação e organização de documentos (ex: termos de
entrega, devolução e termos assinados) em pastas estruturadas por colaborador e número da nota/termo.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import unicodedata


# Expressão regular para identificar o número da nota e o restante do nome
# Exemplo de formatos suportados:
# NOT-0065-Colaborador-Sobrenome-NOTE-96.pdf
# TR-NOT-0085-NOME-COLABORADOR-NOT-0085-TI-Entrega-Ativo.pdf
PADRAO_NOTA = re.compile(
    r"NOT[-_ ]?(\d+)[-_ ]+(.+)",
    re.IGNORECASE,
)

# Palavras-chave e sufixos que devem ser removidos do nome do colaborador
MARCADORES_FINAIS = re.compile(
    r"[-_ ](?:NOTE|NOT|TI|TR|ENTREGA|DEVOLUCAO|"
    r"DEVOLUÇÃO|ASSINADO|ASSINADA)(?:[-_ ]|$)",
    re.IGNORECASE,
)


def normalizar(texto: str) -> str:
    """
    Remove acentos, caracteres especiais e converte para maiúsculas
    para gerar uma chave única de comparação.
    """
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    return re.sub(
        r"[^A-Z0-9]+",
        " ",
        texto.upper()
    ).strip()


def identificar(arquivo: Path):
    """
    Identifica o número da nota e o nome do colaborador a partir do nome do arquivo.
    Retorna um dicionário com os metadados extraídos ou None caso não corresponda ao padrão.
    """
    resultado = PADRAO_NOTA.search(arquivo.stem)

    if not resultado:
        return None

    numero = int(resultado.group(1))
    restante = resultado.group(2)

    marcador = MARCADORES_FINAIS.search(restante)
    if marcador:
        restante = restante[:marcador.start()]

    pessoa = restante.strip(" _-.")
    if not pessoa:
        return None

    pessoa = re.sub(r"[-_ ]+", "-", pessoa).strip("-")

    return {
        "numero": numero,
        "pessoa": pessoa,
        "chave_pessoa": normalizar(pessoa),
        "pasta": f"{numero}-{pessoa}",
    }


def listar_arquivos(pasta: Path):
    """Lista todos os arquivos recursivamente em um diretório."""
    return sorted(
        arquivo
        for arquivo in pasta.rglob("*")
        if arquivo.is_file()
    )


def obter_diretorio_base(caminho_arg: str = None) -> Path:
    """
    Define o diretório base das pastas:
    1. Passado por parâmetro de linha de comando
    2. Definido na variável de ambiente TERMOS_BASE_DIR
    3. Solicitado interativamente ao usuário
    """
    if caminho_arg:
        return Path(caminho_arg).expanduser().resolve()

    env_dir = os.getenv("TERMOS_BASE_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()

    padrao = Path.cwd() / "NOTEBOOKS"
    print(f"\nDiretório base não informado via argumento (--base).")
    try:
        entrada = input(f"Informe o caminho da pasta base [Padrão: {padrao}]: ").strip()
        if entrada:
            return Path(entrada).expanduser().resolve()
    except (EOFError, KeyboardInterrupt):
        print("\nOperação abortada pelo usuário.")
        return padrao

    return padrao


def organizar(base_dir: Path, executar_direto: bool = False):
    """
    Simula e executa a organização dos termos em pastas por colaborador.
    """
    origens = {
        "Entrega de ativos": base_dir / "Entrega de ativos",
        "Devolução de ativos": base_dir / "Devolução de ativos",
        "Assinados": base_dir / "Assinados",
    }
    destino_base = base_dir / "Organizados por colaborador"

    print(f"\nDiretório de trabalho: {base_dir}")

    # Verifica se as pastas de origem existem, caso não exista da o retorno
    pastas_inexistentes = [p for p in origens.values() if not p.is_dir()]
    if pastas_inexistentes:
        print("\nERRO: Uma ou mais pastas de origem não foram encontradas:")
        for p in pastas_inexistentes:
            print(f"  - {p}")
        print("\nNenhuma alteração foi realizada.")
        return

    arquivos_por_origem = {
        categoria: listar_arquivos(pasta)
        for categoria, pasta in origens.items()
    }

    identidades = {}
    for arquivos in arquivos_por_origem.values():
        for arquivo in arquivos:
            dados = identificar(arquivo)
            if dados:
                chave = (dados["numero"], dados["chave_pessoa"])
                identidades.setdefault(chave, dados)

    if not identidades:
        print("Nenhum arquivo com nota e colaborador identificáveis foi encontrado.")
        return

    operacoes = []
    pendentes = []

    print("\n========== SIMULAÇÃO ==========")
    print(f"Notas identificadas: {len(identidades)}")

    for categoria, arquivos in arquivos_por_origem.items():
        for arquivo in arquivos:
            dados = identificar(arquivo)

            if not dados:
                pendentes.append(
                    (categoria, arquivo, "Nome do colaborador não identificado")
                )
                continue

            # Para entrega e devolução, exige o prefixo TR- (TR= termo
            if categoria in ("Entrega de ativos", "Devolução de ativos"):
                if not arquivo.name.upper().startswith("TR-"):
                    pendentes.append(
                        (categoria, arquivo, "Termo sem prefixo TR-")
                    )
                    continue

            pasta_pessoa = destino_base / dados["pasta"]
            pasta_categoria = pasta_pessoa / categoria
            destino_arquivo = pasta_categoria / arquivo.name

            if destino_arquivo.exists():
                pendentes.append(
                    (categoria, arquivo, "Arquivo de destino já existe")
                )
                continue

            operacoes.append(
                (categoria, arquivo, pasta_categoria, destino_arquivo)
            )

            print(f"\nOrigem: {arquivo}")
            print(f"Colaborador: {dados['pessoa']}")
            print(f"Número da nota: {dados['numero']}")
            print(f"Destino: {destino_arquivo}")

    print("\n========== RESUMO DA SIMULAÇÃO ==========")
    print(f"Arquivos preparados: {len(operacoes)}")
    print(f"Arquivos pendentes:  {len(pendentes)}")
    print(f"Destino final:       {destino_base}")

    for categoria, arquivo, motivo in pendentes:
        print(f"PENDENTE [{categoria}]: {arquivo.name} — {motivo}")

    if not operacoes:
        print("\nNenhuma cópia preparada.")
        return

    # Confirmação antes de criar pastas e copiar
    if not executar_direto:
        while True:
            resposta = input(
                "\nDeseja criar as pastas e copiar os documentos? (S/N): "
            ).strip().upper()

            if resposta == "S":
                break

            if resposta == "N":
                print("\nOPERAÇÃO CANCELADA.")
                print("Nenhuma pasta foi criada e nenhum arquivo foi copiado.")
                return

            print("Resposta inválida. Digite S para sim ou N para não.")

    # ======================================================
    # EXECUÇÃO REAL
    # ======================================================
    copiados = 0
    erros = 0

    print("\n========== EXECUÇÃO REAL ==========")

    for categoria, origem, pasta_destino, destino in operacoes:
        try:
            if not origem.is_file():
                print(f"IGNORADO: arquivo não encontrado: {origem}")
                erros += 1
                continue

            if destino.exists():
                print(f"IGNORADO: destino já existe: {destino}")
                erros += 1
                continue

            pasta_destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origem, destino)

            print(f"OK [{categoria}]: {origem.name}")
            copiados += 1

        except OSError as erro:
            print(f"ERRO [{categoria}]: {origem.name}: {erro}")
            erros += 1

    print("\n========== RESULTADO FINAL ==========")
    print(f"Documentos copiados:   {copiados}")
    print(f"Falhas:                {erros}")
    print(f"Documentos pendentes:  {len(pendentes)}")
    print(f"Destino:               {destino_base}")
    print("Os documentos originais foram preservados com sucesso.")


def main():
    parser = argparse.ArgumentParser(
        description="Organizador de Termos de Responsabilidade de TI por Colaborador."
    )
    parser.add_argument(
        "-b", "--base",
        dest="base_dir",
        help="Caminho do diretório base contendo as pastas de origem ('Entrega de ativos', 'Devolução de ativos', 'Assinados').",
        default=None,
    )
    parser.add_argument(
        "-y", "--yes",
        dest="executar_direto",
        action="store_true",
        help="Executa a cópia diretamente sem solicitar confirmação manual.",
    )

    args = parser.parse_args()
    base_path = obter_diretorio_base(args.base_dir)
    organizar(base_path, executar_direto=args.executar_direto)


if __name__ == "__main__":
    main()

#Tady
