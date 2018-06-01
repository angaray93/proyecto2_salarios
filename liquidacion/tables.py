from table import Table
from table.columns import Column, LinkColumn, ImageLink
from table.columns.imagecolumn import ImageColumn
from table.utils import A
from liquidacion.models import *


class LiquidacionMensualTable(Table):
    id = Column(field='id', header='Id')
    #name = Column(field='name')
    #class Meta:
     #   model = Liquidacion
    acciones = LinkColumn(header='ACCIONES', links=[
        ImageLink(viewname='liquidacion:editar_liquidacion', args=(A('id'),)
                  , image='table/images/if_ic_exit_to_app_48px_352328.png', image_title='EDITAR'),
    ])