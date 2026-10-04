import logging
import sqlparse
from pygments import highlight
from pygments.lexers import SqlLexer, GraphQLLexer
from pygments.formatters import TerminalTrueColorFormatter


class PrettySQLFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "sql") and record.sql:
            pretty = sqlparse.format(
                record.sql,
                reindent=True,
                keyword_case="upper",
            )
            colored = highlight(
                pretty, SqlLexer(), TerminalTrueColorFormatter(style="monokai")
            )
            record.sql_pretty = colored.rstrip("\n")
        else:
            record.sql_pretty = getattr(record, "sql", "")

        return super().format(record)


class PrettyGraphQLFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, "query") and record.query:
            colored = highlight(
                record.query,
                GraphQLLexer(),
                TerminalTrueColorFormatter(style="monokai"),
            )
            record.query_pretty = colored.rstrip("\n")
        else:
            record.query_pretty = getattr(record, "query", "")

        return super().format(record)
