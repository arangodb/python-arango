import tempfile
import os
import base64
import typing

class CA_Certificate(object):
    """A CA certificate. If encoded is True the certificate will be automatically base64 decoded"""
    def __init__(
        self, 
        certificate: typing.Union[str, bytes], 
        encoded: bool = True
        ):
        super(CA_Certificate, self).__init__()
        self.certificate = certificate
        if encoded:
            self.certificate = base64.b64decode(self.certificate)
        self.tmp_file = None

    def get_file_path(self):
        """saves the cetificate into a tmp file and returns the file path"""
        if self.tmp_file is not None:
            return self.tmp_file
        _ , self.tmp_file = tempfile.mkstemp(text=True)
        f = open(self.tmp_file, "wb")
        f.write(self.certificate)
        f.close()
        return self.tmp_file 

    def clean(self):
        """erases the tmp_file containing the certificate"""
        if self.tmp_file is not None:
            os.remove(self.tmp_file)
            self.tmp_file = None