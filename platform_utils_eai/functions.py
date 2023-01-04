from datetime import datetime
import os
import zipfile


class AnnotationJob:
    def __init__(self, root_path: str):
        self.root_path = root_path


class CategorizationJob(AnnotationJob):
    def __init__(self, root_path: str, taxonomy: list = None):
        super().__init__(root_path)
        if not taxonomy:
            self.taxonomy = []


def create_annotated_file(folders: dict, filename: str, text: str, annotations: list):
    """

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


def create_folder_structure(root_path: str, timestamp: str) -> dict:
    """

    :param timestamp: momento creazione run - datetime.now().strftime('%d_%m_%y_%H_%M')
    :param root_path: Dev'essere raw string. Percorso completo dove verrà creata o si trova già la cartella runs contenente le varie run
    :return: dizionario con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow
    """
    timenow = datetime.now().strftime('%d_%m_%y_%H_%M')
    tax_folder = f"{root_path}/runs/run_{timenow}/tax"
    xtr_folder = f"{root_path}/runs/run_{timenow}/xtr"
    tax_test_folder = f"{root_path}/runs/run_{timenow}/tax/test"
    tax_ann_folder = f"{root_path}/runs/run_{timenow}/tax/ann"
    xtr_test_folder = f"{root_path}/runs/run_{timenow}/xtr/test"
    xtr_ann_folder = f"{root_path}/runs/run_{timenow}/xtr/ann"
    os.makedirs(f"{root_path}/runs", exist_ok=True)
    os.makedirs(tax_folder, exist_ok=True)
    os.makedirs(xtr_folder, exist_ok=True)
    os.makedirs(tax_test_folder, exist_ok=True)
    os.makedirs(tax_ann_folder, exist_ok=True)
    os.makedirs(xtr_test_folder, exist_ok=True)
    os.makedirs(xtr_ann_folder, exist_ok=True)

    return {
        "tax_test_folder": tax_test_folder,
        "tax_ann_folder": tax_ann_folder,
        "xtr_test_folder": xtr_test_folder,
        "xtr_ann_folder": xtr_ann_folder,
        "tax_folder": tax_folder,
        "xtr_folder": xtr_folder,
        "timenow": timenow

    }


def create_libraries_zip(folders: dict, timestamp: str, split: float = 0.8):
    """

    :param timestamp: momento creazione run - datetime.now().strftime('%d_%m_%y_%H_%M')
    :param folders: dict con percorsi delle cartelle tax_test, tax_ann, xtr_test, xtr_ann, tax, xtr + timenow. Creato con create_folder_structure
    :param split: split tra librerie di train e test
    :return:
    """
    for i in [folders["tax_folder"], folders["xtr_folder"]]:
        os.chdir(i)
        # create train lib
        with zipfile.ZipFile(f'{i.split("/")[-1]}_train_lib{timestamp}.zip', 'w') as zipObj:
            for root, dirs, files in os.walk(f'ann'):
                for f in files[:int(len(files) * split)]:
                    zipObj.write(os.path.join(root, f))
            for root, dirs, files in os.walk(f'test'):
                for f in files[:int(len(files) * split)]:
                    zipObj.write(os.path.join(root, f))
        # create test lib
        with zipfile.ZipFile(f'{i.split("/")[-1]}_test_lib{timestamp}.zip', 'w') as zipObj:
            for root, dirs, files in os.walk(f'ann'):
                for f in files[int(len(files) * split):]:
                    zipObj.write(os.path.join(root, f))
            for root, dirs, files in os.walk(f'test'):
                for f in files[int(len(files) * split):]:
                    zipObj.write(os.path.join(root, f))
        os.chdir("../../..")


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
