class ServicesConstants :
    """
    Constants for working with services
    """

    @property
    def NSSM_DOWNLOAD_URL(self) :
        return 'https://nssm.cc/release/nssm-2.24.zip' # The URL to use for downloading NSSM when needed

SERVICE_CONST = ServicesConstants()