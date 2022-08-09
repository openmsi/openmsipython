class FurnaceConstants :
    """
    Constants for Laser Shock Lab stuff and the associated FileMaker Database
    """
    @property
    def SPREADSHEET_KEY_FILE(self) :
        return "C:/Users/cathe/Downloads/furnace-index-card-data-3663bd4611da.json" #private key location for the furnace spreadsheet service account
    @property
    def SPREADSHEET_NAME(self) :
        return "Furnace Index Card Form (Responses)" #Name of the particular spreadsheet to access

FURNACE_CONST = FurnaceConstants()