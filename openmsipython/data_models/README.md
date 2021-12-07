## Data Modeling

The Open MSI / DMREF projects link and track materials, the processes that created them, and measurements performed on them using a data model built on [the Python binding](https://github.com/CitrineInformatics/gemd-python) for [Citrine Informatics' Graphical Expression of Materials Data (GEMD)](https://citrineinformatics.github.io/gemd-docs/) implemented as part of `openmsipython`.

### Laser Shock

The Laser Shock Lab tracks its materials and experimental data using a [FileMaker Pro 18 Advanced](https://www.claris.com/filemaker/pro/) database. The `openmsipython` code includes routines to read that database using a [Python wrapper around the RESTful FileMaker Data API](https://github.com/davidhamann/python-fmrest) and convert and link its entries as a set of GEMD entities.

To see examples of those created GEMD entities, you can run the following command from just inside the `openmsipython` repo (or as appropriate from any other location):

`python -m openmsipython.data_models.laser_shock.laser_shock_lab`

This will create a new directory called `gemd_data_model_dumps` containing the following files :
1. a "`LaserShockLab.log`" log file with information about what the `openmsipython` code discovered in the FileMaker database
1. several files called "`LaserShock*_1.json`" which are example JSON representations of each type of GEMD object created directly from a layout in the FileMaker database. 
1. several files called "`*_material_history.json`" which are detailed JSON representations of the complete material history for example objects that are represented as MaterialRuns within the data model. These files list every Run, Spec, and Template used to represent those MaterialRun objects and their provenance as determined from the FileMaker database.

Note that running any of this code requires access to the Johns Hopkins University network either locally or through a VPN, as well as access to the specific FileMaker database used by the Laser Shock Lab. CI tests for this portion of the code use a dictionary of a few example FileMaker records instead of reading the real database.
