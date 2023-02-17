"""
This module containes functions to create annotated libraries to be imported into EAI Platform
"""
from datetime import datetime
import os
import zipfile
from pathlib import Path
from typing import Generator, Union
import splitfolders
import random
import shutil
import json
import csv


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


def make_json_from_csv(csvFilePath: Union[str, Path], jsonFilePath: Union[str, Path], primary_key: str):
    """
    Make a json file out of a csv creating a dictionary of {"pk":"all row content"} objects.

    :param csvFilePath:
    :param jsonFilePath:
    :param primary_key: column of the csv that will be treated as pk
    :return:
    """
    # create a dictionary
    data = {}

    # Open a csv reader called DictReader
    with open(csvFilePath, encoding='utf-8') as csvf:
        csvReader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for rows in csvReader:
            # Assuming a column named 'No' to
            # be the primary key
            key = rows[primary_key]
            data[key] = rows

    # Open a json writer, and use the json.dumps()
    # function to dump data
    with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
        jsonf.write(json.dumps(data, indent=4))


def create_annotated_file(folders: dict, filename: Union[str, Path], text: str, annotations: list):
    """
    Crea un file di testo e un file di annotazione nella directory `folders` con i nomi specificati.

    La funzione prende in input un dizionario `folders` che contiene i percorsi alle cartelle necessarie per la
    creazione dei file, il nome del file senza estensione, il testo da annotare e una lista di annotazioni associate
    al testo. La funzione crea un file di testo nella cartella `tax_test_folder` con il nome `{filename}.txt` e un file
    di annotazione nella cartella `tax_ann_folder` con il nome `{filename}.ann`.

    :param folders: Dizionario contenente i percorsi alle cartelle necessarie per la creazione dei file.
    :param filename: Nome del file senza estensione.
    :param text: Testo da annotare.
    :param annotations: Lista di annotazioni associate al testo.
    :return: Nessun valore di ritorno.
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


def create_folder_structure(root_path: Union[str, Path]) -> dict:
    """
    Creates folder structure to be used by :func:`create_libraries_zip`

    :param root_path: Percorso assoluto dove verrà creata o si trova già la cartella runs contenente le varie run
    :return: dizionario con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow
    """
    timenow = datetime.now().strftime('%d_%m_%y_%H_%M')
    tax_test_folder = Path(f"{root_path}/runs/run_{timenow}/tax/test")
    tax_ann_folder = Path(f"{root_path}/runs/run_{timenow}/tax/ann")
    xtr_test_folder = Path(f"{root_path}/runs/run_{timenow}/xtr/test")
    xtr_ann_folder = Path(f"{root_path}/runs/run_{timenow}/xtr/ann")

    tax_test_folder.mkdir(parents=True, exist_ok=True)
    tax_ann_folder.mkdir(parents=True, exist_ok=True)
    xtr_test_folder.mkdir(parents=True, exist_ok=True)
    xtr_ann_folder.mkdir(parents=True, exist_ok=True)

    tax_ann_split_folder = Path(tax_test_folder.parent / "ann_split")
    tax_test_split_folder = Path(tax_test_folder.parent / "test_split")
    xtr_ann_split_folder = Path(xtr_test_folder.parent / "ann_split")
    xtr_test_split_folder = Path(xtr_test_folder.parent / "test_split")

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


def split_folder_no_cat(src_folder, dest_folder1, dest_folder2, split_ratio):
    """
    Split contents of src folder into 2 separate folders for train and test randomly. Used when there are no folder
    for cats already available (all files are in one folder, ie: no annotations available).

    :param src_folder:
    :param dest_folder1:
    :param dest_folder2:
    :param split_ratio:
    :return:
    """
    # Get a list of files in the src_folder
    filenames = [filename for filename in os.listdir(src_folder) if
                 os.path.isfile(os.path.join(src_folder, filename))]

    # Shuffle the list of files
    random.seed(1337)
    random.shuffle(filenames)

    # Split the list of files into two parts
    split_index = int(split_ratio * len(filenames))
    first_part = filenames[:split_index]
    second_part = filenames[split_index:]

    # Move the files in the first part to dest_folder1
    for filename in first_part:
        shutil.move(os.path.join(src_folder, filename), os.path.join(dest_folder1, filename))

    # Move the files in the second part to dest_folder2
    for filename in second_part:
        shutil.move(os.path.join(src_folder, filename), os.path.join(dest_folder2, filename))


def create_libraries_zip(folders: dict):
    """
    Creates libraries zip files to ready to be imported to the Platform. Both ann and test files should be split in
    train and val folders and inside there should be a folder for each class (as created by split-folders package)

    :param folders: dict con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow. Creato con create_folder_structure
    :return:
    """
    pass
    # tax_ann_folder_empty = not any(folders["tax_ann_folder"].iterdir())
    # if not tax_ann_folder_empty:
    #     has_category_folders = any(item.is_dir() for item in folders["tax_ann_folder"].glob("*"))
    #
    #     if has_category_folders:
    #         splitfolders.ratio(folders["tax_ann_folder"], output=Path(folders["tax_ann_split_folder"]),
    #                            seed=1337, ratio=(.8, .2), move=True)
    #         splitfolders.ratio(folders["tax_test_folder"], output=Path(folders["tax_test_split_folder"]),
    #                            seed=1337, ratio=(.8, .2), move=True)
    #
    #     else:
    #         Path(folders["tax_ann_split_folder"] / "train").mkdir(exist_ok=True)
    #         Path(folders["tax_ann_split_folder"] / "val").mkdir(exist_ok=True)
    #         Path(folders["tax_test_split_folder"] / "train").mkdir(exist_ok=True)
    #         Path(folders["tax_test_split_folder"] / "val").mkdir(exist_ok=True)
    #
    #         split_folder_no_cat(folders["tax_ann_folder"], folders["tax_ann_split_folder"] / "train",
    #                             folders["tax_ann_split_folder"] / "val", 0.8)
    #         split_folder_no_cat(folders["tax_test_folder"], folders["tax_test_split_folder"] / "train",
    #                             folders["tax_test_split_folder"] / "val", 0.8)
    #
    #     shutil.rmtree(folders["tax_ann_folder"])
    #     shutil.rmtree(folders["tax_test_folder"])
    #
    # #TODO deal with splitting extraction library if it works differently than tax
    # xtr_ann_folder_empty = not any(folders["xtr_ann_folder"].iterdir())
    # if not xtr_ann_folder_empty:
    #     splitfolders.ratio(folders["xtr_ann_folder"], output=Path(folders["xtr_ann_split_folder"]),
    #                        seed=1337, ratio=(.8, .2), move=True)
    #     splitfolders.ratio(folders["xtr_test_folder"], output=Path(folders["xtr_test_split_folder"]),
    #                        seed=1337, ratio=(.8, .2), move=True)
    #     shutil.rmtree(folders["xtr_ann_folder"])
    #     shutil.rmtree(folders["xtr_test_folder"])
    #
    # #  Create TAX library zip
    # print(os.getcwd())
    # os.chdir(folders["tax_folder"])
    # print(os.getcwd())
    #
    # tax_train_annotations = Path(folders["tax_folder"] / "ann_split" / "train").glob(f'**/*.ann')
    # tax_train_tests = Path(folders["tax_folder"] / "test_split" / "train").glob(f'**/*.txt')
    # tax_val_annotations = Path(folders["tax_folder"] / "ann_split" / "val").glob(f'**/*.ann')
    # tax_val_tests = Path(folders["tax_folder"] / "test_split" / "val").glob(f'**/*.txt')
    #
    # train_zip_name = f"{folders['tax_folder'].name}_train_lib_{folders['timenow']}"
    # val_zip_name = f"{folders['tax_folder'].name}_val_lib_{folders['timenow']}"
    # # create train lib
    # zip_loop(tax_train_annotations, tax_train_tests, train_zip_name)
    #
    # # create test lib
    # zip_loop(tax_val_annotations, tax_val_tests, val_zip_name)
    #
    # #  Create XTR library zip
    # # TODO xtr zip


def split_tax_library(folders: dict, train_pct: float):
    """
    Split the taxonomy annotation and test data folders into training and validation sets,
    using the given train percentage. The input is a dictionary of paths to the input and output
    folders, with the keys "tax_ann_folder", "tax_ann_split_folder", "tax_test_folder",
    and "tax_test_split_folder". The function uses the splitfolders package to split the data,
    or a custom split_folder_no_cat function if the taxonomy annotation folder does not have
    category subfolders. The input train percentage is a float between 0 and 1. The output is None,
    but the function creates the split folders and removes the original input folders.

    .. code-block::
       :caption: Example

        folders = {
             "tax_ann_folder": Path("path/to/tax_ann_folder"),
             "tax_ann_split_folder": Path("path/to/tax_ann_split_folder"),
             "tax_test_folder": Path("path/to/tax_test_folder"),
             "tax_test_split_folder": Path("path/to/tax_test_split_folder")
        }
        split_tax_library(folders, train_pct=0.8)

    :param folders: A dictionary of paths to the input and output folders, with the keys
        "tax_ann_folder", "tax_ann_split_folder", "tax_test_folder", and "tax_test_split_folder".
    :type folders: dict
    :param train_pct: The percentage of data to use for training, a float between 0 and 1.
    :type train_pct: float
    :raises FileNotFoundError: If the taxonomy annotation folder is empty.
    :returns: None

    """

    val_pct = 1-train_pct
    tax_ann_folder_empty = not any(folders["tax_ann_folder"].iterdir())
    if not tax_ann_folder_empty:
        has_category_folders = any(item.is_dir() for item in folders["tax_ann_folder"].glob("*"))

        if has_category_folders:
            splitfolders.ratio(folders["tax_ann_folder"], output=Path(folders["tax_ann_split_folder"]),
                               seed=1337, ratio=(train_pct, val_pct), move=True)
            splitfolders.ratio(folders["tax_test_folder"], output=Path(folders["tax_test_split_folder"]),
                               seed=1337, ratio=(train_pct, val_pct), move=True)

        else:
            Path(folders["tax_ann_split_folder"] / "train").mkdir(exist_ok=True)
            Path(folders["tax_ann_split_folder"] / "val").mkdir(exist_ok=True)
            Path(folders["tax_test_split_folder"] / "train").mkdir(exist_ok=True)
            Path(folders["tax_test_split_folder"] / "val").mkdir(exist_ok=True)

            split_folder_no_cat(folders["tax_ann_folder"], folders["tax_ann_split_folder"] / "train",
                                folders["tax_ann_split_folder"] / "val", train_pct)
            split_folder_no_cat(folders["tax_test_folder"], folders["tax_test_split_folder"] / "train",
                                folders["tax_test_split_folder"] / "val", train_pct)

        shutil.rmtree(folders["tax_ann_folder"])
        shutil.rmtree(folders["tax_test_folder"])
    else:
        raise FileNotFoundError("tax folder is empty")


def zip_loop(zip_path: Path, ann_list: list, test_list: list, zip_name: str):
    """
    Crea un archivio ZIP contenente i file delle liste `ann_list` e `test_list`, posizionandoli all'interno delle
    rispettive cartelle ann e test.

   :param zip_path: Percorso della directory in cui creare l'archivio ZIP.
   :param ann_list: Lista di percorsi ai file di annotazione.
   :param test_list: Lista di percorsi ai file di test.
   :param zip_name: Nome dell'archivio ZIP.
   :return: Nessun valore di ritorno.
    """
    with zipfile.ZipFile(f'{zip_path}\\{zip_name}.zip', 'w') as zipObj:
        for f in ann_list:
            zipObj.write(f, arcname=f"ann/{zip_name}/test/{f.name}")
            # zipObj.write(f, arcname=f"test/{train_zip_name}/ann/{f.name}.txt")
        for f in test_list:
            zipObj.write(f, arcname=f"test/{zip_name}/test/{f.name}")


def create_tax_library_zip(folders: dict):
    """
    Crea due archivi ZIP contenenti i file di annotazione e di test per le cartelle di addestramento e di validazione
    della tassonomia specificata nella directory `folders`.

    La funzione utilizza la funzione `split_tax_library()` per creare le cartelle di addestramento e di validazione,
    quindi crea due archivi ZIP chiamati `train_lib_{time}` e `val_lib_{time}`, rispettivamente contenenti i file di
    annotazione e di test delle cartelle di addestramento e di validazione.

    :param folders: Dizionario contenente i percorsi alle cartelle necessarie per la creazione delle librerie.
    :return: Nessun valore di ritorno.

    :param folders:
    :return:
    """
    split_tax_library(folders, 0.8)

    tax_train_annotations = list(Path(folders["tax_folder"] / "ann_split" / "train").glob(f'*.ann'))
    tax_train_tests = list(Path(folders["tax_folder"] / "test_split" / "train").glob(f'*.txt'))
    tax_val_annotations = list(Path(folders["tax_folder"] / "ann_split" / "val").glob(f'*.ann'))
    tax_val_tests = list(Path(folders["tax_folder"] / "test_split" / "val").glob(f'*.txt'))

    train_zip_name = f"{folders['tax_folder'].name}_train_lib_{folders['timenow']}"
    val_zip_name = f"{folders['tax_folder'].name}_val_lib_{folders['timenow']}"

    # os.chdir(folders["tax_folder"])
    # print(os.getcwd())

    # create train lib
    zip_loop(folders["tax_folder"], tax_train_annotations, tax_train_tests, train_zip_name)

    # create test lib
    zip_loop(folders["tax_folder"], tax_val_annotations, tax_val_tests, val_zip_name)


def create_xtr_library_zip(folders: dict):
    pass


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
