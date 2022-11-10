import graphene

import regression.schema


class Query(regression.schema.Query):
    pass


schema = graphene.Schema(query=Query)