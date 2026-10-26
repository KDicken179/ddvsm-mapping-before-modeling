# Data

The datasets are not redistributed in this repository. Download them from their original sources and place them in this folder.

| Case | Dataset | Source | File to place here |
|---|---|---|---|
| A | E-Commerce Shipping Data ("Customer Analytics"), prachi13 | https://www.kaggle.com/datasets/prachi13/customer-analytics | `Train.csv` |
| B | DataCo Smart Supply Chain for Big Data Analysis, Constante, Silva, & Pereira (2019), Version 5 | https://doi.org/10.17632/8gx2fvg2k6.5 | `DataCoSupplyChainDataset.csv` |

Notes

- Case A in the paper uses records with `ID <= 8999` (8,999 records), the labeled subset of the public copy used during the study. The script applies this filter by default (`--max-id 8999`). Use `--max-id 0` to run on all 10,999 records; results will differ slightly.
- In Case A, `Reached.on.Time_Y.N = 1` means the shipment was **late**.
- The DataCo file is read with `latin-1` encoding.
