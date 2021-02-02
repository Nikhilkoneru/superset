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
"""Contains the logic to create cohesive forms on the explore view"""
from typing import List

from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm
from flask_babel import lazy_gettext as _
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, IntegerField, SelectField, StringField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
import datetime
from superset import app, db, security_manager
from superset.forms import (
    CommaSeparatedListField,
    filter_not_empty_values,
    JsonListField,
)
from superset.models.core import Database

config = app.config


class IgceUploadForm(DynamicForm):
    # pylint: disable=E0211
    def csv_allowed_dbs() -> List[Database]:  # type: ignore
        csv_enabled_dbs = (
            db.session.query(Database).filter_by(allow_csv_upload=True).all()
        )
        return [
            csv_enabled_db
            for csv_enabled_db in csv_enabled_dbs
            if IgceUploadForm.at_least_one_schema_is_allowed(csv_enabled_db)
        ]

    @staticmethod
    def at_least_one_schema_is_allowed(database: Database) -> bool:
        """
        If the user has access to the database or all datasource
            1. if schemas_allowed_for_csv_upload is empty
                a) if database does not support schema
                    user is able to upload csv without specifying schema name
                b) if database supports schema
                    user is able to upload csv to any schema
            2. if schemas_allowed_for_csv_upload is not empty
                a) if database does not support schema
                    This situation is impossible and upload will fail
                b) if database supports schema
                    user is able to upload to schema in schemas_allowed_for_csv_upload
        elif the user does not access to the database or all datasource
            1. if schemas_allowed_for_csv_upload is empty
                a) if database does not support schema
                    user is unable to upload csv
                b) if database supports schema
                    user is unable to upload csv
            2. if schemas_allowed_for_csv_upload is not empty
                a) if database does not support schema
                    This situation is impossible and user is unable to upload csv
                b) if database supports schema
                    user is able to upload to schema in schemas_allowed_for_csv_upload
        """
        if security_manager.can_access_database(database):
            return True
        schemas = database.get_schema_access_for_csv_upload()
        if schemas and security_manager.get_schemas_accessible_by_user(
            database, schemas, False
        ):
            return True
        return False

    department = StringField(
        _("Department"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        default="Department of Treasury"
    )
    agency = StringField(
        _("Agency"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
        default="IRS"
    )
    solicitation = StringField(
        _("Solicitation"),
        validators=[DataRequired()],
        widget=BS3TextFieldWidget(),
    )
    location = FileField(
        _("File"),
        validators=[
            FileRequired()
        ],
    )
