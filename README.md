# drawio-bom

Simple tool to extract specially crafted data from `draw.io` diagrams into csv *BOM* (Bill Of Materials).

# Installation

Just `pip install .`.

# Usage

In your `draw.io` diagram, add data to object:

- Right click on object -> `Edit Data...`
- Enter property name: `BOM_ID` press `Enter`
- Enter property value - something that will be shown in your BOM as component id.
- Optionally - if the amount of this component is different that 1 (eg. 0.5m of cable,
  4 screws), add property `BOM_AMOUNT` and fill with proper amount

Run this tool:

```bash
$ drawio-bom my_diagram.drawio
BOM_ID;BOM_AMOUNT
battery;1
res_100;1
led_red;3
```
