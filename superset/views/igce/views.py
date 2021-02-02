# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import os
import tempfile
from typing import TYPE_CHECKING

from flask import flash, g, redirect
from flask_appbuilder import expose, SimpleFormView
from flask_appbuilder.api import BaseApi, expose
from superset.views.base import (
    BaseView
)
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access
from flask_babel import lazy_gettext as _
from werkzeug.wrappers import Response
from wtforms.fields import StringField
from wtforms.validators import ValidationError

import superset.models.core as models
from superset import app, db, is_feature_enabled
from superset.connectors.sqla.models import SqlaTable
from superset.constants import MODEL_VIEW_RW_METHOD_PERMISSION_MAP, RouteMethod
from superset.exceptions import CertificateException
from superset.sql_parse import Table
from superset.typing import FlaskResponse
from superset.utils import core as utils
from superset.views.base import DeleteMixin, SupersetModelView, YamlExportMixin

from .forms import IgceUploadForm

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage  # pylint: disable=unused-import

config = app.config
stats_logger = config["STATS_LOGGER"]


def upload_stream_write(form_file_field: "FileStorage", path: str) -> None:
    chunk_size = app.config["UPLOAD_CHUNK_SIZE"]
    with open(path, "bw") as file_description:
        while True:
            chunk = form_file_field.stream.read(chunk_size)
            if not chunk:
                break
            file_description.write(chunk)


class IgceUploadView(SimpleFormView):
    form = IgceUploadForm
    route_base = "/igce/upload"
    form_template = "superset/form_view/igce_view/upload.html"
    form_title = _("IGCE Upload Form")

    def form_get(self, form: IgceUploadForm) -> None:
        pass

    def form_post(self, form: IgceUploadForm) -> Response:
        pass


class IGCE(BaseView):
    route_base = "/igce/"

    @expose("/")
    def render(self):
        return self.render_template("superset/sample.html")
