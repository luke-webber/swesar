# swesar
> Terminal client for downloading Sentinel images from [Swea Portal](https://swea.rymdstyrelsen.se/portal/).

## Usage Example

Downloading a single product using the ESA product name:

```sh
python swesar.py S1A_IW_GRDH_1SDV_20180224T162111_20180224T162136_020751_0238FE_48D1
```

Downloading multiple products using downloaded product cart from the [ESA Copernicus Open Access Hub](https://scihub.copernicus.eu/):

```sh
python swesar.py products.meta4
```

