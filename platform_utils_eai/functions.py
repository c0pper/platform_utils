"""
This module containes functions to create annotated libraries to be imported into EAI Platform
"""
from datetime import datetime
import os
import zipfile
from pathlib import Path
from typing import Generator


# class AnnotationJob:
#     def __init__(self, root_path: str):
#         self.root_path = root_path
#
#
# class CategorizationJob(AnnotationJob):
#     def __init__(self, root_path: str, taxonomy: list = None):
#         super().__init__(root_path)
#         if not taxonomy:
#             self.taxonomy = []


def create_annotated_file(folders: dict, filename: str, text: str, annotations: list):
    """
    Generic annotation creation function, needs to be worked on

    :param folders: dict con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow. Creato con create_folder_structure
    :param filename: nome file senza estensione
    :param text: testo annotato
    :param annotations: lista di annotazioni associate al testo
    :return:
    """

    # categorization
    tax_count = 1
    with open(f"{folders['tax_test_folder']}/{filename}.txt", 'w', encoding="utf-8") as file:
        # print(txt)
        file.write(text)
    file.close()

    with open(f"{folders['tax_ann_folder']}/{filename}.ann", 'a', encoding="utf-8") as ann:
        for a in annotations:
            ann.write(f"C{tax_count}		{a}\n")
            tax_count += 1
    ann.close()


def create_folder_structure(root_path: str) -> dict:
    """
    Creates folder structure to be used by :func:`create_libraries_zip`

    :param root_path: Dev'essere raw string. Percorso completo dove verrà creata o si trova già la cartella runs contenente le varie run
    :return: dizionario con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow
    """
    timenow = datetime.now().strftime('%d_%m_%y_%H_%M')
    tax_test_folder = Path(f"{root_path}/runs/run_{timenow}/tax/test")
    tax_ann_folder = Path(f"{root_path}/runs/run_{timenow}/tax/ann")
    xtr_test_folder = Path(f"{root_path}/runs/run_{timenow}/xtr/test")
    xtr_ann_folder = Path(f"{root_path}/runs/run_{timenow}/xtr/ann")

    tax_ann_split_folder = Path(tax_test_folder.parent / "ann_split")
    tax_test_split_folder = Path(tax_test_folder.parent / "test_split")
    xtr_ann_split_folder = Path(xtr_test_folder.parent / "ann_split")
    xtr_test_split_folder = Path(xtr_test_folder.parent / "test_split")

    tax_test_folder.mkdir(parents=True, exist_ok=True)
    tax_ann_folder.mkdir(parents=True, exist_ok=True)
    xtr_test_folder.mkdir(parents=True, exist_ok=True)
    xtr_ann_folder.mkdir(parents=True, exist_ok=True)

    tax_ann_split_folder.mkdir(parents=True, exist_ok=True)
    tax_test_split_folder.mkdir(parents=True, exist_ok=True)
    xtr_ann_split_folder.mkdir(parents=True, exist_ok=True)
    xtr_test_split_folder.mkdir(parents=True, exist_ok=True)

    return {
        "tax_test_folder": tax_test_folder,
        "tax_ann_folder": tax_ann_folder,
        "xtr_test_folder": xtr_test_folder,
        "xtr_ann_folder": xtr_ann_folder,
        "tax_folder": tax_test_folder.parent,
        "xtr_folder": xtr_test_folder.parent,
        "tax_ann_split_folder": tax_ann_split_folder,
        "tax_test_split_folder": tax_test_split_folder,
        "xtr_ann_split_folder": xtr_ann_split_folder,
        "xtr_test_split_folder": xtr_test_split_folder,
        "timenow": timenow
    }


def create_libraries_zip(folders: dict, timestamp: str):
    """
    Creates libraries zip files to ready to be imported to the Platform. Both ann and test files should be split in
    train and val folders and inside there should be a folder for each class (as created by split-folders package)

    :param timestamp: momento creazione run - datetime.now().strftime('%d_%m_%y_%H_%M')
    :param folders: dict con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow. Creato con create_folder_structure
    :return:
    """

    def zip_loop(ann_list: Generator, test_list: Generator, zip_name: str):
        with zipfile.ZipFile(f'{zip_name}.zip', 'w') as zipObj:
            for f in list(ann_list):
                zipObj.write(f, arcname=f"ann/{zip_name}/test/{f.name}")
                # zipObj.write(f, arcname=f"test/{train_zip_name}/ann/{f.name}.txt")
            for f in list(test_list):
                zipObj.write(f, arcname=f"test/{zip_name}/test/{f.name}")

    for i in [folders["tax_folder"], folders["xtr_folder"]]:
        os.chdir(i)
        print(os.getcwd())

        tax_train_annotations = Path(i / "ann_split" / "train").glob(f'**/*.ann')
        tax_train_tests = Path(i / "test_split" / "train").glob(f'**/*.txt')
        tax_val_annotations = Path(i / "ann_split" / "val").glob(f'**/*.ann')
        tax_val_tests = Path(i / "test_split" / "val").glob(f'**/*.txt')

        train_zip_name = f"{i.name}_train_lib_{timestamp}"
        val_zip_name = f"{i.name}_val_lib_{timestamp}"
        # create train lib
        zip_loop(tax_train_annotations, tax_train_tests, train_zip_name)

        # create test lib
        zip_loop(tax_val_annotations, tax_val_tests, val_zip_name)


def normalize_fucked_encoding(string: str, qmark_char: str = " ") -> str:
    """
    reference table: https://www.i18nqa.com/debug/utf8-debug.html

    :param string: testo da correggere
    :param qmark_char: carattere default in caso di �
    :return: testo corretto
    """
    char_to_replace = {
        "�": qmark_char,
        "â‚¬": "€",
        "â€š": "‚",
        "â€ž": "„",
        "â€¦": "…",
        "â€¡": "‡",
        "â€°": "‰",
        "â„¢": "™",
        "â€¹": "‹",
        "â€˜": "'",
        "â€™": "'",
        "â€œ": "“",
        "â€¢": "•",
        "â€“": "–",
        "â€”": "—",
        "Ëœ": "˜",
        "Å¡": "š",
        "â€º": "›",
        "Æ’": "ƒ",
        "Å“": "œ",
        "Ë†": "ˆ",
        "Å’": "Œ",
        "Å½": "Ž",
        "Å¾": "ž",
        "Å¸": "Ÿ",
        "Â¡": "¡",
        "Â¢": "¢",
        "Â£": "£",
        "Â¤": "¤",
        "Â¥": "¥",
        "Â¦": "¦",
        "Â§": "§",
        "Â¨": "¨",
        "Â©": "©",
        "Âª": "ª",
        "Â«": "«",
        "Â¬": "¬",
        "Â­": "­",
        "Â®": "®",
        "Â¯": "¯",
        "Â°": "°",
        "Â±": "±",
        "Â²": "²",
        "Â³": "³",
        "Â´": "´",
        "Âµ": "µ",
        "Â¶": "¶",
        "Â·": "·",
        "Â¸": "¸",
        "Â¹": "¹",
        "Âº": "º",
        "Â»": "»",
        "Â¼": "¼",
        "Â½": "½",
        "Â¾": "¾",
        "Â¿": "¿",
        "â€": "†",
        "Ã€": "À",
        "Ã‚": "Â",
        "Ãƒ": "Ã",
        "Ã„": "Ä",
        "Ã…": "Å",
        "Ã†": "Æ",
        "Ã‡": "Ç",
        "Ãˆ": "È",
        "Ã‰": "É",
        "ÃŠ": "Ê",
        "Ã‹": "Ë",
        "ÃŒ": "Ì",
        "Ã": "Í",
        "ÃŽ": "Î",
        "Ã": "Ï",
        "Ã": "Ð",
        "Ã‘": "Ñ",
        "Ã’": "Ò",
        "Ã“": "Ó",
        "Ã”": "Ô",
        "Ã•": "Õ",
        "Ã–": "Ö",
        "Ã—": "×",
        "Ã˜": "Ø",
        "Ã™": "Ù",
        "Ãš": "Ú",
        "Ã›": "Û",
        "Ãœ": "Ü",
        "Ãž": "Þ",
        "ÃŸ": "ß",
        "Ã¡": "á",
        "Ã¢": "â",
        "Ã£": "ã",
        "Ã¤": "ä",
        "Ã¥": "å",
        "Ã¦": "æ",
        "Ã§": "ç",
        "Ãµ": "õ",
        "Ã¶": "ö",
        "Ã·": "÷",
        "Ã¸": "ø",
        "Ã¹": "ù",
        "Ãº": "ú",
        "Ã»": "û",
        "Ã¼": "ü",
        "Ã½": "ý",
        "Ã¾": "þ",
        "Ã¿": "ÿ",
        "Ã¨": "è",
        "Ã©": "é",
        "Ãª": "ê",
        "Ã«": "ë",
        "Ã¬": "ì",
        "Ã­": "í",
        "Ã®": "î",
        "Ã¯": "ï",
        "Ã°": "ð",
        "Ã±": "ñ",
        "Ã²": "ò",
        "Ã³": "ó",
        "Ã´": "ô",
        "â€": "'",
        "Ã": "à",
        "Ã": "Ý",
        "Ã": "Á",
        "Å": "Š",
        "Â": " ",
        "ś": "",
        "ť": "",
        "\"": "'"
    }
    for key, value in char_to_replace.items():
        string = string.replace(key, value)
    return string
