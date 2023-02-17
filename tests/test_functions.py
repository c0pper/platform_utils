import pytest
from pathlib import Path
import shutil
import json
from platform_utils_eai.functions import create_folder_structure, create_tax_library_zip, make_json_from_csv, create_annotated_file
import csv
import os


@pytest.fixture
def root_path():
    # before test - create resource
    root_path = Path("./tests/test_root")
    root_path.mkdir(exist_ok=True)
    yield root_path
    # after test - remove resource
    # shutil.rmtree(root_path)


@pytest.fixture
def csv_path():
    """Return a temporary CSV file path."""
    csv_path = Path("tests/NLP with Disaster Tweets.csv")
    yield csv_path


@pytest.fixture
def json_path(root_path):
    """Return a temporary JSON file path."""
    yield root_path / "NLP with Disaster Tweets.json"


def test_make_json_from_csv(tmp_path: Path):
    # Create a CSV file for testing
    csv_data = [
        {'name': 'Alice', 'age': '25'},
        {'name': 'Bob', 'age': '30'},
        {'name': 'Charlie', 'age': '35'},
    ]
    csv_file_path = tmp_path / 'test.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'age'])
        writer.writeheader()
        writer.writerows(csv_data)

    # Call the function being tested
    json_file_path = tmp_path / 'test.json'
    primary_key = 'name'
    make_json_from_csv(csv_file_path, json_file_path, primary_key)

    # Check that the JSON file was created and has the expected content
    assert json_file_path.exists()
    with open(json_file_path, encoding='utf-8') as f:
        json_data = json.load(f)
        assert len(json_data) == len(csv_data)
        for row in csv_data:
            key = row[primary_key]
            assert key in json_data
            assert json_data[key] == row


def test_create_folder_structure(root_path):
    folder_structure = create_folder_structure(root_path)

    # Assert the returned dictionary contains the expected keys
    assert set(folder_structure.keys()) == {"tax_test_folder", "tax_ann_folder", "xtr_test_folder", "xtr_ann_folder",
                                            "tax_folder", "xtr_folder", "tax_ann_split_folder", "tax_test_split_folder",
                                            "xtr_ann_split_folder", "xtr_test_split_folder", "timenow"}

    # Assert the folders have been created with the correct paths
    assert folder_structure["tax_test_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/tax/test")
    assert folder_structure["tax_ann_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/tax/ann")
    assert folder_structure["xtr_test_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/xtr/test")
    assert folder_structure["xtr_ann_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/xtr/ann")
    assert folder_structure["tax_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/tax")
    assert folder_structure["xtr_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/xtr")
    assert folder_structure["tax_ann_split_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/tax/ann_split")
    assert folder_structure["tax_test_split_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/tax/test_split")
    assert folder_structure["xtr_ann_split_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/xtr/ann_split")
    assert folder_structure["xtr_test_split_folder"] == Path(f"{root_path}/runs/run_{folder_structure['timenow']}/xtr/test_split")

    # Assert the folders have been created
    assert folder_structure["tax_test_folder"].exists()
    assert folder_structure["tax_ann_folder"].exists()
    assert folder_structure["xtr_test_folder"].exists()
    assert folder_structure["xtr_ann_folder"].exists()
    assert folder_structure["tax_folder"].exists()
    assert folder_structure["xtr_folder"].exists()
    assert folder_structure["tax_ann_split_folder"].exists()
    assert folder_structure["tax_test_split_folder"].exists()
    assert folder_structure["xtr_ann_split_folder"].exists()
    assert folder_structure["xtr_test_split_folder"].exists()

# @pytest.mark.skip
def test_create_annotated_file_no_annotations(root_path, csv_path, json_path):
    folders = create_folder_structure(root_path)
    pk = "id"

    make_json_from_csv(csv_path, json_path, pk)

    with open(json_path, encoding="utf-8") as j:
        data = json.load(j)

    for k, v in data.items():
        # print(k, v)
        create_annotated_file(folders, v["id"], v["text"], [])


def test_create_libraries_zip_with_csv_no_annotations(root_path, json_path, csv_path):
    folders = create_folder_structure(root_path)
    pk = "id"

    make_json_from_csv(csv_path, json_path, pk)

    with open(json_path, encoding="utf-8") as j:
        data = json.load(j)

    for k, v in data.items():
        create_annotated_file(folders, v["id"], v["text"], [])
    create_tax_library_zip(folders)

    # Check that the ZIP files were created and have the expected content
    assert os.path.exists(folders["tax_folder"] / f"{folders['tax_folder'].name}_train_lib_{folders['timenow']}.zip")
    assert os.path.exists(folders["tax_folder"] / f"{folders['tax_folder'].name}_val_lib_{folders['timenow']}.zip")

    # Extract the train ZIP and check its contents
    train_zip_name = Path(f"{folders['tax_folder'].name}_train_lib_{folders['timenow']}.zip")
    shutil.unpack_archive(folders["tax_folder"] / train_zip_name, folders["tax_folder"] / "unpack_train", 'zip')

    train_ann_zip_path = folders["tax_folder"] / "unpack_train" / "ann" / train_zip_name.stem / "test"
    train_test_zip_path = folders["tax_folder"] / "unpack_train" / "test" / train_zip_name.stem / "test"
    print(train_ann_zip_path / "1.ann")
    print(os.getcwd())
    assert os.path.exists(train_ann_zip_path / "1.ann")
    assert os.path.exists(train_test_zip_path / "1.txt")
    with open(train_ann_zip_path / "1.ann") as f:
        assert f.read() == ''
    with open(train_test_zip_path / "1.txt") as f:
        assert f.read() == 'Our Deeds are the Reason of this #earthquake May ALLAH Forgive us all'

    # Extract the val ZIP and check its contents
    val_zip_name = Path(f"{folders['tax_folder'].name}_val_lib_{folders['timenow']}.zip")
    shutil.unpack_archive(folders["tax_folder"] / val_zip_name, folders["tax_folder"] / "unpack_val", 'zip')

    val_ann_zip_path = folders["tax_folder"] / "unpack_val" / "ann" / val_zip_name.stem / "test"
    val_test_zip_path = folders["tax_folder"] / "unpack_val" / "test" / val_zip_name.stem / "test"
    assert not os.path.exists(val_ann_zip_path / "1.ann")
    assert not os.path.exists(val_test_zip_path / "1.txt")
