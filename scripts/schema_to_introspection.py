import json
import sys

from graphql import build_schema, get_introspection_query, graphql_sync


def main(sdl_path: str, json_path: str) -> None:
    sdl = open(sdl_path).read()
    schema = build_schema(sdl)
    result = graphql_sync(schema, get_introspection_query())
    with open(json_path, "w") as f:
        json.dump({"data": result.data}, f, indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
