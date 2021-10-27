# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
from tempfile import NamedTemporaryFile

import SimpleITK as sitk
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth
from odoo import fields, models
from requests.auth import HTTPBasicAuth

_logger = logging.getLogger(__name__)


class MedicalImagingEndpoint(models.Model):

    _inherit = "medical.imaging.endpoint"

    connection_type = fields.Selection(
        selection_add=[("dicom-wado-rs", "Dicom Wado")]
    )

    def _get_images_from_series(self, report, series):
        for endpoint in self:
            if endpoint.connection_type != "dicom-wado-rs":
                continue
            if endpoint.user:
                auth = HTTPBasicAuth(endpoint.user, endpoint.password)
                session = create_session_from_auth(auth)
                client = DICOMwebClient(url=endpoint.url, session=session)
            for serie in series:
                instances = client.retrieve_series(
                    study_instance_uid=serie.imaging_study_id.instance_uid,
                    series_instance_uid=serie.instance_uid,
                )
                for im in instances:
                    try:
                        image_bytes = self._convert_image(im)
                        filename = "file_%s.jpg" % im.InstanceNumber
                        report.add_image_attachment(
                            name=filename, datas=base64.b64encode(image_bytes)
                        )
                    except Exception:
                        _logger.debug(
                            "This instance could not be converted",
                            exc_info=True,
                        )
                        continue

    def _convert_image(self, dicom_image, file_format="jpg", new_width=None):
        try:
            with NamedTemporaryFile(suffix=".dcm") as file:
                dicom_image.save_as(file.name)
                image_file_reader = sitk.ImageFileReader()
                # only read DICOM images
                image_file_reader.SetImageIO("GDCMImageIO")
                image_file_reader.SetFileName(file.name)
                image_file_reader.ReadImageInformation()
                image_size = list(image_file_reader.GetSize())
                if len(image_size) == 3 and image_size[2] == 1:
                    image_size[2] = 0
                image_file_reader.SetExtractSize(image_size)
                image = image_file_reader.Execute()
            if new_width:
                original_size = image.GetSize()
                original_spacing = image.GetSpacing()
                new_spacing = [
                    (original_size[0] - 1)
                    * original_spacing[0]
                    / (new_width - 1)
                ] * 2
                new_size = [
                    new_width,
                    int(
                        (original_size[1] - 1)
                        * original_spacing[1]
                        / new_spacing[1]
                    ),
                ]
                image = sitk.Resample(
                    image1=image,
                    size=new_size,
                    transform=sitk.Transform(),
                    interpolator=sitk.sitkLinear,
                    outputOrigin=image.GetOrigin(),
                    outputSpacing=new_spacing,
                    outputDirection=image.GetDirection(),
                    defaultPixelValue=0,
                    outputPixelType=image.GetPixelID(),
                )
            # If a single channel image, rescale to [0,255]. Also modify the
            # intensity values based on the photometric interpretation. If
            # MONOCHROME2 (minimum should be displayed as black) we don't need to
            # do anything, if image has MONOCRHOME1 (minimum should be displayed as
            # white) we flip # the intensities. This is a constraint imposed by ITK
            # which always assumes MONOCHROME2.
            if image.GetNumberOfComponentsPerPixel() == 1:
                image = sitk.RescaleIntensity(image, 0, 255)
                if (
                    image_file_reader.GetMetaData("0028|0004").strip()
                    == "MONOCHROME1"
                ):
                    image = sitk.InvertIntensity(image, maximum=255)
                image = sitk.Cast(image, sitk.sitkUInt8)
            with NamedTemporaryFile(suffix="." + file_format) as output_file:
                sitk.WriteImage(image, output_file.name)
                result = output_file.read()
            return result
        except BaseException:
            raise
