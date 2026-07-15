import strawberry


@strawberry.type
class Query:
    test: str = strawberry.field(lambda: "Hello, world!")


schema = strawberry.Schema(query=Query)
