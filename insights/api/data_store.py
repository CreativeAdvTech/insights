import frappe

from insights.decorators import insights_whitelist, validate_type
from insights.insights.doctype.insights_table_v3.insights_table_v3 import get_table_name


@insights_whitelist()
@validate_type
def get_data_store_tables(data_source=None, search_term=None, limit=100):
    Table = frappe.qb.DocType("Insights Table v3")
    DataSource = frappe.qb.DocType("Insights Data Source v3")

    tables = (
        frappe.qb.from_(Table)
        .left_join(DataSource)
        .on(Table.data_source == DataSource.name)
        .select(
            Table.name,
            Table.table,
            Table.label,
            Table.data_source,
            Table.last_synced_on,
            DataSource.database_type,
        )
        .where(
            (Table.stored == 1)
            & (
                Table.data_source == data_source
                if data_source
                else Table.data_source.like("%")
            )
            & (
                (Table.label == search_term if search_term else Table.label.like("%"))
                | (Table.table == search_term if search_term else Table.table.like("%"))
            )
        )
        .limit(limit)
        .run(as_dict=True)
    )

    ret = []
    for table in tables:
        ret.append(
            frappe._dict(
                {
                    "name": table.name,
                    "label": table.label,
                    "table_name": table.table,
                    "data_source": table.data_source,
                    "database_type": table.database_type,
                    "last_synced_on": table.last_synced_on,
                }
            )
        )
    return ret


@insights_whitelist()
@validate_type
def import_table(data_source: str, table_name: str):
    frappe.only_for("Insights Admin")
    name = get_table_name(data_source, table_name)
    table_doc = frappe.get_doc("Insights Table v3", name)
    table_doc.import_to_warehouse(overwrite=True)
