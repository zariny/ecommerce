from django.core.exceptions import ValidationError
from django.db import connection


class ProductClassGraphValidator:
    """
    Validates ProductClass DAG constraints.
    """

    @classmethod
    def validate_edge(cls, parent_id: int, child_id: int):
        if parent_id == child_id:
            raise ValidationError("A ProductClass cannot inherit from itself.")

        if cls.check_cycle(parent_id, child_id):
            raise ValidationError("This relation creates a cycle.")

    @classmethod
    def check_cycle(cls, parent_id: int, child_id: int) -> bool:  #  use cte
        """
        Checks whether adding parent -> child creates a cycle.

        A cycle exists if child can already reach parent.
        """

        sql = """
        WITH RECURSIVE descendants AS (
            SELECT
                child_id
            FROM products_productclassedge
            WHERE parent_id = %s

            UNION

            SELECT
                edge.child_id
            FROM products_productclassedge edge
            INNER JOIN descendants d
                ON edge.parent_id = d.child_id
        )
        SELECT 1
        FROM descendants
        WHERE child_id = %s
        LIMIT 1;
        """

        with connection.cursor() as cursor:
            cursor.execute(
                sql,
                [
                    child_id,
                    parent_id,
                ],
            )
            return cursor.fetchone() is not None
