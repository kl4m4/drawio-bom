from typing import Dict, Union, List, Optional
from typing_extensions import Annotated
from abc import ABC, abstractmethod
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
import logging
from dataclasses import dataclass
import typer

logger = logging.getLogger(__name__)

class DrawioCell:
    pass

class DrawioDiagram:
    pass

@dataclass
class BOMItem:
    reference_id: str
    amount: Union[int, float]
    labels: List[str]
    ids: List[str]

class FileReader(ABC):
    @abstractmethod
    def read_file(self, file: Path) -> ET.ElementTree:
        pass

class PlainDrawioFileReader(FileReader):
    def read_file(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        if "compressed" in root.attrib.keys() and root.attrib['compressed'] == "true":
            raise NotImplementedError("Cannot parse compressed diagrams")
        return tree


class DrawioDocument:
    def __init__(self, xml_tree: ET.ElementTree):
        self.root = xml_tree.getroot()

    def get_bom(self, id_key: str = "BOM_ID", amount_key: str = "BOM_AMOUNT") -> List[BOMItem]:
        ret = []
        for item in self.root.iter():
            if item.tag == "object":
                logger.info(f"got object, attrs: {item.attrib}")
                if id_key in item.attrib.keys():
                    amount = 1
                    if amount_key in item.attrib.keys():
                        amount = float(item.attrib[amount_key])
                    ret.append(BOMItem(item.attrib[id_key], amount, [item.attrib['label']], [item.attrib['id']]))

        # Sum amount by id
        summed = DrawioDocument._sum_by_id(ret)
        as_list: list[BOMItem] = list(summed.values())

        # Try to 'int-emize' amounts
        def is_int(x):
            x = float(x)
            if x.is_integer():
                return int(x)
            return x

        for item in as_list:
            item.amount = is_int(item.amount)
        return as_list

    def _sum_by_id(bom: List[BOMItem]) -> List[BOMItem]:
        logger.debug(f"post processing - summing by id")
        processed_bom = {}
        for entry in bom:
            if entry.reference_id in processed_bom:
                logger.debug(f"id {entry.reference_id} already in processed bom")
                processed_bom[entry.reference_id].amount += entry.amount
                processed_bom[entry.reference_id].labels.extend(entry.labels)
                processed_bom[entry.reference_id].ids.extend(entry.ids)

            else:
                logger.debug(f"adding id {entry.reference_id} to processed bom")
                processed_bom[entry.reference_id] = BOMItem(
                    reference_id=entry.reference_id,
                    amount=entry.amount,
                    labels=entry.labels.copy(),
                    ids=entry.ids.copy()
                )
        return processed_bom


def main(
        input_file: Path = typer.Argument(..., help="Input file in one of draw.io formats"),
        output_file: Optional[Path] = typer.Option(None, help="Optional output file instead of printing to stdout"),
        id_key: Optional[str] = typer.Option("BOM_ID", help="Name of attribute with BOM part reference (eg. a part number)"),
        amount_key: Optional[str] = typer.Option("BOM_AMOUNT", help="Name of attribute with BOM part count")
    ):
    """
    Generates BOM list from given INPUT_FILE in one of draw.io file formats.
    """
    if input_file.suffix != ".drawio":
        typer.echo("Currently only plain .drawio files are supported", err=True)
        sys.exit(1)

    # To be developed later - different reader for .drawio.svg, .drawio.png etc...
    file_reader = PlainDrawioFileReader()
    
    try:
        doc = DrawioDocument(file_reader.read_file(input_file))
    except NotImplementedError as err:
        typer.echo(err, err=True)
        sys.exit(1)

    bom = doc.get_bom(id_key=id_key, amount_key=amount_key)
    print(f"{id_key};{amount_key}")
    for item in bom:
        print(f"{item.reference_id};{item.amount}")


def entrypoint():
    typer.run(main)

if __name__ == "__main__":
    typer.run(main)