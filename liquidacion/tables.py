from table import Table
from table.columns import Column, LinkColumn, ImageLink
from table.columns.imagecolumn import ImageColumn
from table.utils import A
from liquidacion.models import *


class LiquidacionMensualTable(Table):
    id = Column(field='id', header='Codigo')
    funcionario = Column(field='funcionario', header='Funcionario')
    mes = Column(field='mes', header='Mes')
    #class Meta:
     #   model = Liquidacion
    acciones = LinkColumn(header='Editar', links=[
        ImageLink(viewname='liquidacion:editar_liquidacion', args=(A('id'),)
                  , image='table/images/if_ic_exit_to_app_48px_352328.png', image_title='EDITAR'),
    ])