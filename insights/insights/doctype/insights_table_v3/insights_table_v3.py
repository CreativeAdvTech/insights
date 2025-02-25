# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


from hashlib import md5

import frappe
from frappe.model.document import Document, bulk_insert

from insights.insights.doctype.insights_data_source_v3.data_warehouse import Warehouse
from insights.utils import InsightsDataSourcev3


class InsightsTablev3(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        data_source: DF.Link
        label: DF.Data
        last_synced_on: DF.Datetime | None
        stored: DF.Check
        table: DF.Data
    # end: auto-generated types

    def autoname(self):
        self.name = get_table_name(self.data_source, self.table)

    @staticmethod
    def bulk_create(data_source: str, tables: list[str]):
        table_docs = []
        for table in tables:
            doc = frappe.new_doc("Insights Table v3")
            doc.name = get_table_name(data_source, table)
            doc.data_source = data_source
            doc.table = table
            doc.label = table
            table_docs.append(doc)

        bulk_insert("Insights Table v3", table_docs, ignore_duplicates=True)

    @staticmethod
    def get_ibis_table(data_source, table_name, use_live_connection=False):
        from insights.insights.doctype.insights_team.insights_team import (
            apply_table_restrictions,
            check_table_permission,
        )

        check_table_permission(data_source, table_name)

        if not use_live_connection:
            wt = Warehouse().get_table(data_source, table_name)
            t = wt.get_ibis_table(import_if_not_exists=True)
        else:
            ds = InsightsDataSourcev3.get_doc(data_source)
            t = ds.get_ibis_table(table_name)

        t = apply_table_restrictions(t, data_source, table_name)
        return t

    @frappe.whitelist()
    def import_to_warehouse(self, overwrite=False):
        frappe.only_for("Insights Admin")
        wt = Warehouse().get_table(self.data_source, self.table)
        wt.import_remote_table(overwrite=overwrite)


def get_table_name(data_source, table):
    return md5((data_source + table).encode()).hexdigest()[:10]
