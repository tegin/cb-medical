# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import json
import logging

from openupgradelib import openupgrade

from odoo.addons.http_routing.models.ir_http import slugify

_logger = logging.getLogger(__name__)


def _get_storage_vals(code, record):
    protocol = "odoofs"
    options = record
    if record["backend_type"] == "filesystem":
        protocol = "file"
        options = {}

    if record["backend_type"] == "ftp":
        protocol = "ftp"
        options = {
            "host": record["ftp_server"],
            "port": record["ftp_server"],
            "username": record["ftp_login"],
            "password": record["ftp_password"],
        }
    if record["backend_type"] == "sftp":
        protocol = "sftp"
        options = {
            "host": record["sftp_host"],
            "ssh_kwargs": {
                "port": record["sftp_port"],
            },
        }
        if record["sftp_auth_method"] == "pwd":
            options["ssh_kwargs"].update(
                {
                    "username": record["sftp_user"],
                    "password": record["sftp_password"],
                }
            )
        elif record["sftp_auth_method"] == "ssh_key":
            _logger.warning(
                "SSH Key requires a PrivateKey file, but we are "
                "providing a string. Please check the migration."
            )
            options["ssh_kwargs"].update(
                {
                    "pkey": record["sftp_private_key"],
                }
            )
    if record["backend_type"] == "s3":
        protocol = "s3"
        options = {
            "endpoint_url": record["aws_host"],
            "key": record["aws_access_key_id"],
            "secret": record["aws_secret_access_key"],
        }
    return {
        "name": record["name"],
        "code": code,
        "protocol": protocol,
        "options": json.dumps(options, default=str),
        "directory_path": record["directory_path"],
    }


@openupgrade.migrate()
def migrate(env, version):
    storage_backend_id = int(
        env["ir.config_parameter"]
        .sudo()
        .get_param("storage.diagnostic.report.image.backend_id")
    )
    openupgrade.logged_query(
        env.cr,
        """
        SELECT * FROM storage_backend
        WHERE id = %s
        """,
        (storage_backend_id,),
    )
    column_names = [desc[0] for desc in env.cr.description]
    storage_backend_records = []
    for row in env.cr.fetchall():
        storage_backend_records.append(dict(zip(column_names, row)))
    record = storage_backend_records[0]
    defaults = json.loads(record.pop("server_env_defaults"))
    for key in defaults:
        record[key.split("_env_default")[0]] = defaults[key]
    fs_storage = env["fs.storage"]
    code = slugify(record.get("name")).replace("-", "_")
    if fs_storage.search([("code", "=", code)]):
        code = "%s_%d" % (code, record["id"])

    storage = fs_storage.create(_get_storage_vals(code, record))
    openupgrade.logged_query(
        env.cr,
        f"""
        INSERT INTO ir_attachment (
            name,
            type,
            res_model,
            res_id,
            create_uid,
            create_date,
            write_uid,
            write_date,
            mimetype,
            store_fname,
            file_size,
            checksum,
            index_content,
            public,
            access_token,
            company_id,
            fs_storage_id,
            fs_url,
            fs_storage_code,
            fs_filename
        )
        SELECT
            sf.name,
            'binary' as type,
            'medical.diagnostic.report.image' as res_model,
            mdri.id as res_id,
            sf.create_uid,
            sf.create_date,
            sf.write_uid,
            sf.write_date,
            sf.mimetype,
            CONCAT('{storage.code}://', sf.relative_path) as store_fname,
            sf.file_size,
            sf.checksum,
            'image' as index_content,
            NULL as public,
            NULL as access_token,
            sf.company_id,
            {storage.id} as fs_storage_id,
            NULL as fs_url,
            {storage.code} as fs_storage_code,
            sf.name as fs_filename

        FROM storage_file sf
        INNER JOIN medical_diagnostic_report_image mdri ON mdri.file_id = sf.id
        WHERE sf.backend_id = {record["id"]}
        """,
    )
