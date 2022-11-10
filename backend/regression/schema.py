import graphene
from graphene_django import DjangoObjectType, DjangoListField

from regression.models import Dataset, Axis, Cell


class DatasetType(DjangoObjectType):
    class Meta:
        model = Dataset


class AxisType(DjangoObjectType):
    class Meta:
        model = Axis


class CellType(DjangoObjectType):
    class Meta:
        model = Cell


class CreateDataset(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    dataset = graphene.Field(DatasetType)

    @staticmethod
    def mutate(root, info, name):
        dataset = Dataset.objects.create(user=info.context.user, name=name)
        return CreateDataset(dataset=dataset)


class CreateAxis(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        dataset_id = graphene.Int()
        column = graphene.Boolean()

    axis = graphene.Field(AxisType)

    @staticmethod
    def mutate(root, info, name, dataset_id, column):
        axis = Axis.objects.create(user=info.context.user, name=name, dataset_id=dataset_id, column=column)
        return CreateAxis(axis=axis)


class PushRow(graphene.Mutation):
    class Arguments:
        dataset_id = graphene.Int()
        column_ids = graphene.List(graphene.Int)
        values = graphene.List(graphene.Float)

    row = graphene.Field(AxisType)
    cells = graphene.List(CellType)

    @staticmethod
    def mutate(root, info, dataset_id, column_ids, values):
        row = Axis.objects.create(user=info.context.user, dataset_id=dataset_id, column=False)
        cells = []
        for column_id, value in zip(column_ids, values):
            cells.append(Cell(user=info.context.user, row=row, column_id=column_id, value=value, dataset_id=dataset_id))
        cells = Cell.objects.bulk_create(cells)
        return PushRow(row=row, cells=cells)


class Query(graphene.ObjectType):
    datasets = DjangoListField(DatasetType)
    axes = DjangoListField(AxisType, dataset_id=graphene.Int(), is_column=graphene.Boolean())
    cells = DjangoListField(CellType, dataset_id=graphene.Int(), column_id=graphene.Int(), row_id=graphene.Int())
    create_dataset = CreateDataset.Field()

    @staticmethod
    def resolve_datasets(root, info):
        return Dataset.objects.filter(user=info.context.user)

    @staticmethod
    def resolve_axes(root, info, dataset_id, is_column):
        return Axis.objects.filter(user=info.context.user, dataset=dataset_id, column=is_column)

    @staticmethod
    def resolve_cells(root, info, dataset_id, column_id=None, row_id=None):
        cells = Cell.objects.filter(user=info.context.user, dataset=dataset_id)
        if column_id:
            cells = cells.filter(column=column_id)
        if row_id:
            cells = cells.filter(row=row_id)
        return cells