# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt


import frappe
from frappe.model.document import Document

from insights.insights.doctype.insights_data_source_v3.data_warehouse import (
    DataWarehouse,
)


class InsightsTablev3(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        from insights.insights.doctype.insights_table_column.insights_table_column import (
            InsightsTableColumn,
        )

        columns: DF.Table[InsightsTableColumn]
        data_source: DF.Link
        label: DF.Data
        last_synced_on: DF.Datetime | None
        name: DF.Int | None
        table: DF.Data
    # end: auto-generated types

    def before_insert(self):
        if is_duplicate(self):
            raise frappe.DuplicateEntryError

    @staticmethod
    def create(data_source, table_name):
        doc = frappe.new_doc("Insights Table v3")
        doc.data_source = data_source
        doc.table = table_name
        doc.label = table_name
        if not is_duplicate(doc):
            doc.db_insert()

    @staticmethod
    def get_ibis_table(data_source, table_name, use_live_connection=False):
        return DataWarehouse().get_table(
            data_source,
            table_name,
            use_live_connection=use_live_connection,
        )

    @frappe.whitelist()
    def import_to_data_warehouse(self):
        frappe.only_for("System Manager")
        DataWarehouse().import_remote_table(
            self.data_source,
            self.table,
            force=True,
        )


def is_duplicate(doc):
    return frappe.db.exists(
        "Insights Table v3",
        {
            "data_source": doc.data_source,
            "table": doc.table,
        },
    )
