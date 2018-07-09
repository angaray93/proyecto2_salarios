import datetime
from django.db.models import Sum, Max, Q
from decimal import Decimal, ROUND_HALF_UP
from django.db import models, utils
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.functions import Coalesce

from sueldos.settings import DATE_INPUT_FORMATS

ConstanteType_OPTIONS = (
    ('D', 'Debito'),
    ('C', 'Credito'),
)

Modalidad_OPTIONS = (
    ('M' , 'Mensual'),
    ('S' , 'Semestral'),
    ('O' , 'Otros'),
)

MES_OPTIONS = (
    ('Enero' , 'Enero'),
    ('Febrero' , 'Febrero'),
    ('Marzo' , 'Marzo'),
    ('Abril' , 'Abril'),
    ('Mayo' , 'Mayo'),
    ('Junio' , 'Junio'),
    ('Julio' , 'Julio'),
    ('Agosto' , 'Agosto'),
    ('Septiembre' , 'Septiembre'),
    ('Octubre' , 'Octubre'),
    ('Noviembre' , 'Noviembre'),
    ('Diciembre' , 'Diciembre'),

)

def validar_vacio(value):
    convertido = value.replace(" ", "")
    if not value:
        raise ValidationError(
            ('Debe completar este campo'),
        )
    return value


def validar_nombre(value):
    convertido = value.replace(" ", "")
    if convertido.isalpha() is False:
        raise ValidationError(
            ('%(value)s no es valido, favor ingrese un valor sin numeros ni simbolos'),
            params={'value': value},
        )

class Funcionario(models.Model):
    idFuncionario = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=50, default='')
    nombres = models.CharField(max_length=50, default='')
    apellidos = models.CharField(max_length=50, default='')
    fechanacimiento = models.DateField(verbose_name='Fecha de Nacimiento')
    direccion = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=50, default='')
    telefono = models.CharField(max_length=50, default='')
    cantHijos = models.IntegerField(verbose_name='Cantidad de Hijos')
    #-----------------------------------Relationships-----------------------------------------#
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='fk_funcionario_usuario_fk')
    grado = models.ForeignKey('GradoUniversitario', on_delete=models.DO_NOTHING, related_name='fk_funcionario_grado' )
    estadocivil = models.ForeignKey('EstadoCivil', on_delete=models.DO_NOTHING, related_name='fk_funcionario_ecivil', verbose_name='Estado Civil')
    ciudadnacimiento = models.ForeignKey('Ciudad', on_delete=models.DO_NOTHING, related_name='fk_funcionario_ciudad', verbose_name='Lugar de Nacimiento')

    class Meta:
        ordering = ["apellidos"]
        verbose_name_plural = "Funcionarios"

    def __str__(self):
        return '%s %s' % (self.nombres, self.apellidos)


class Movimiento(models.Model):
    idmovimiento = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, default='', blank=True, null=True)
    tipo = models.ForeignKey('MovimientoType', on_delete=models.DO_NOTHING, related_name='fk_movimiento_tipo', blank=False)
    motivo = models.ForeignKey('MovimientoMotivo', on_delete=models.DO_NOTHING, related_name='fk_movimiento_motivo', blank=False)
    formapago = models.CharField(max_length=1,choices=Modalidad_OPTIONS, default='M', blank=False)
    fechainicio = models.DateField(blank=False)
    fechafin = models.DateField(blank=True, null=True)
    esPrimero = models.BooleanField(default=True)
    horaEntrada = models.TimeField(blank=True, null=True)
    horaSalida = models.TimeField(blank=True, null=True)
    tieneAguinaldo = models.BooleanField(default=False)
    tieneVacaciones = models.BooleanField(default=False)
    funcion = models.CharField(max_length=99, default='', validators=[validar_nombre], blank=False)
    familia = models.IntegerField(blank=True, null=True, default=1)
    #------------------------------------Relationships-----------------------------------------#
    ffinanciamiento = models.ForeignKey('FuenteFinanciamiento', on_delete=models.DO_NOTHING, default=1)
    funcionario = models.ForeignKey('Funcionario', on_delete=models.DO_NOTHING, related_name='fk_movimiento_funcionario')
    categoria_salarial = models.ForeignKey('CategoriaSalarial', on_delete=models.DO_NOTHING,
                                           related_name='fk_movimiento_categoriasalarial', blank=False)
    division = models.ForeignKey('Division', on_delete=models.DO_NOTHING, related_name='fk_movimiento_division', blank=False)
    og = models.ForeignKey('Objeto_De_Gasto', on_delete=models.DO_NOTHING, related_name='fk_movimiento_og')
    movimiento_padre = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True)
    estado = models.ForeignKey('State', on_delete=models.DO_NOTHING, related_name='fk_movimiento_estado')


class Pago(models.Model):
    id = models.AutoField(primary_key=True)
    monto = models.IntegerField()
    pagado = models.BooleanField(default=False)
    # -----------------------------------Relationships-----------------------------------------#
    mes = models.ForeignKey('Mes', on_delete=models.DO_NOTHING, default=1)
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='fk_pago_movimiento')

    class Meta:
        verbose_name_plural = "Pagos"
        unique_together = (('mes', 'movimiento'),)


class FuenteFinanciamiento(models.Model):
    id = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, default='', unique=True)
    numero = models.IntegerField()

    class Meta:
        ordering = ["descripcion"]
        verbose_name_plural = "Fuentes de Financiamiento"

    def __str__(self):
        return 'Fuente %s  - %s ' % (self.numero, self.descripcion)


class Objeto_De_Gasto(models.Model):
    id_og = models.AutoField(primary_key=True)
    concepto = models.CharField(max_length=100, default='', validators=[validar_nombre], unique=True)
    numero = models.IntegerField(unique=True)

    class Meta:
        ordering = ["numero"]
        verbose_name_plural = "Objetos de Gasto"

    def __str__(self):
        return '%s %s' % (self.numero, self.concepto)


class Departamento(models.Model):
    iddepartamento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    # -----------------------------------Relationships-----------------------------------------#
    director = models.ForeignKey('Funcionario', on_delete=models.DO_NOTHING, related_name='fk_departamento_funcionario')

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Departamentos"

    def __str__(self):
        return '%s' % (self.nombre)


class Division(models.Model):
    iddivision = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    # -----------------------------------Relationships-----------------------------------------#
    jefe = models.ForeignKey('Funcionario', on_delete=models.DO_NOTHING, related_name='fk_division_funcionario')
    departamento = models.ForeignKey('Departamento', on_delete=models.DO_NOTHING, related_name='fk_division_departamento')

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Divisiones"

    def __str__(self):
        return '%s %s %s' % (self.nombre,' - ', self.departamento.nombre)


class Aguinaldo(models.Model):
    id = models.AutoField(primary_key=True)
    anho = models.IntegerField(default=datetime.datetime.today().year)
    cantidad_meses = models.DecimalField(default=0, max_digits=3, decimal_places=1, blank=True, null=True)
    acumulado = models.DecimalField(default=0, max_digits=12, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(default=0, max_digits=12, decimal_places=2, blank=True, null=True)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='aguinaldo_movimiento')

    def calculo_acumulado(self, idliqhaber):
        liquidacion = Liquidacionhaber.objects.get(pk=idliqhaber)
        if self.movimiento.motivo.nombre != 'Contrato':
            resultado = liquidacion.subTotal / Decimal(12)
        else:
            pago = liquidacion.pago
            resultado = pago.monto / 12
        return round(resultado)

    def calculo_total(self):
        resultado = self.acumulado
        return resultado


class Pais(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Paises"

    def __str__(self):
        return '%s ' % (self.nombre)


class Ciudad(models.Model):
    idciudad = models.AutoField(primary_key=True)
    nombreciudad = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True, verbose_name='Nombre de la Ciudad')
    # -----------------------------------Relationships-----------------------------------------#
    pais = models.ForeignKey('Pais', on_delete=models.CASCADE, related_name='fk_ciudad_pais')

    class Meta:
        ordering = ["nombreciudad"]
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return '%s %s %s' % (self.nombreciudad, ' - ', self.pais)


class CategoriaSalarial(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, default='', unique=True)
    tipo = models.CharField(max_length=30, default='')
    cargo = models.CharField(max_length=50, default='', validators=[validar_nombre])
    asignacion = models.IntegerField()

    class Meta:
        ordering = ["codigo"]
        verbose_name_plural = "Categorias Salariales"

    def __str__(self):
        return '%s ' % self.codigo


class EstadoCivil(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Estados Civiles"

    def __str__(self):
        return '%s ' % (self.nombre)


class GradoUniversitario(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Grado Universitario"

    def __str__(self):
        return '%s ' % (self.nombre)


class Vacaciones(models.Model):
    id = models.AutoField(primary_key=True)
    anho = models.IntegerField(default=datetime.datetime.today().year)
    inicio = models.DateTimeField()
    fin = models.DateTimeField(blank=True, null=True)
    diasobtenidos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diasusados = models.IntegerField(default=0)
    dias_restantes = models.IntegerField(default=0)
    monto = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name= 'vacaciones_movimiento')

    def calculo_diasobtenidos(self):
        cantidad_mes = Decimal(30/12)
        resultado = self.diasobtenidos + cantidad_mes
        return resultado

    def calculo_diasusados(self):
        cantidad_mes = self.vacacionesusadas_set.usados
        resultado = self.diasusados + cantidad_mes
        return resultado

    def calculo_diasrestantes(self):
        resultado = self.diasobtenidos - self.diasusados
        return resultado

    def calculo_monto(self):
        cantidad_mes = self.movimiento.categoria_salarial.asignacion / 30
        resultado = self.monto + cantidad_mes
        return resultado


class Vacacionesusadas(models.Model):
    id = models.AutoField(primary_key=True)
    diasusados = models.IntegerField(default=0)
    # -----------------------------------Relationships-----------------------------------------#
    vacaciones = models.ForeignKey('Vacaciones', on_delete=models.CASCADE, null=True, blank=True)
    mes = models.ForeignKey('Mes', on_delete=models.DO_NOTHING)


class Mes(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.IntegerField(default=0)
    nombre = models.CharField(max_length=50, default='')
    year = models.IntegerField(default=2018)

    class Meta:
        unique_together = (('nombre', 'year'),)

    def __str__(self):
        return '%s - %s' % (self.nombre, self.year)


class Constante(models.Model):
    id = models.AutoField(primary_key=True)
    finito = models.BooleanField(default=False)
    cantidad_veces = models.IntegerField(blank=True, null=True)
    ocurrencias = models.IntegerField(blank=True, null=True, default=0)
    monto = models.IntegerField(blank=True, null=True, default=0)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='fk_constante_movimiento')
    tipo = models.ForeignKey('ConstanteType', on_delete=models.CASCADE, related_name='fk_constante_tipo')

    class Meta:
        unique_together = (('movimiento', 'tipo'),)

    '''def calcular_monto(self):
        if self.tipo.porcentaje != 0 and self.tipo.porcentaje is not None:
            return ((self.movimiento.categoria_salarial.asignacion * self.tipo.porcentaje) / Decimal(100))
        else:
            return self.monto'''


class ConstanteType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    tipo = models.CharField(max_length=1, choices=ConstanteType_OPTIONS)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Constante"

    def __str__(self):
        if self.porcentaje is not None :
            return '%s %s %s %s' % (self.nombre ,' - ', self.porcentaje, '%')
        else:
            return '%s ' % (self.nombre)


class MovimientoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Movimiento"

    def __str__(self):
        return '%s ' % (self.nombre)


class MovimientoMotivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Motivos de Movimiento"

    def __str__(self):
        return '%s ' % (self.nombre)


class DocumentoRespaldatorio(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, default='')
    fechaemision = models.DateField()
    quienfirma = models.CharField(max_length=50, default='')
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.DO_NOTHING,
                                               related_name='fk_movimiento_documentorespaldatorio')
    tipo = models.ForeignKey('DocumentoType', on_delete=models.CASCADE,
                             related_name='fk_documentorespaldatorio_tipo')
    autoridadfirmante = models.ForeignKey('AutoridadFirmante', on_delete=models.CASCADE,
                              related_name='fk_documentorespaldatorio_autoridadfirmante')

    class Meta:
        verbose_name_plural = "Documentos Respaldatorios"

    def __str__(self):
        return '%s ' % (self.codigo)


class DocumentoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Documento"

    def __str__(self):
        return '%s ' % (self.nombre)


class AutoridadFirmante(models.Model):
    id = models.AutoField(primary_key=True)
    cargo = models.CharField(max_length=50, validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["cargo"]
        verbose_name_plural = "Autoridades Firmantes"

    def __str__(self):
        return '%s ' % (self.cargo)


class Liquidacion(models.Model):
    id = models.AutoField(primary_key=True)
    fechacreacion = models.DateTimeField()
    ultimamodificacion = models.DateTimeField()
    mes = models.ForeignKey('Mes', on_delete=models.DO_NOTHING, default=1)
    total_debito = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, default=0)
    total_credito = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True, default= 0)
    total_liquidacion = models.IntegerField(default=0, blank=True, null=True)
    inicio_periodo = models.DateTimeField()
    fin_periodo = models.DateTimeField(null=True, blank=True)
    dias_trabajados = models.IntegerField(default=0, blank=True, null=True)
    vacaciones_usadas = models.IntegerField(default=0, blank=True)
    #-----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_liq_funcionario')
    estado_actual = models.ForeignKey('State', on_delete=models.CASCADE, related_name='fk_liquidacion_estado')
    tipo = models.ForeignKey('LiquidacionType', on_delete=models.CASCADE, related_name='fk_liquidacion_tipo')
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_liquidacion_user')
    motivo = models.ForeignKey('LiquidacionMotivo', on_delete=models.CASCADE, related_name='fk_liquidacion_motivo', default=1, null=True, blank=True)

    #class Meta:
    #    unique_together = (('funcionario', 'mes'),)

    def calculo_total_debito(self):
        suma_total_debito = self.liquidacionhaber_set.filter(liquidacion=self.pk)\
            .aggregate(total_debito=Coalesce(
                Sum(models.F('monto_debito')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['total_debito'] or 0
        return suma_total_debito

    def calculo_total_credito(self):
        suma_total_credito = self.liquidacionhaber_set.filter(liquidacion=self.pk)\
            .aggregate(total_credito=Coalesce(
                Sum(models.F('monto_credito')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['total_credito'] or 0
        return suma_total_credito

    def calcular_total_liquidacion(self):
        total = round((self.total_credito - self.total_debito), 0)
        return total


class Liquidacionhaber(models.Model):
    id = models.AutoField(primary_key=True)
    haber = models.ForeignKey('Haber', on_delete=models.CASCADE)
    liquidacion = models.ForeignKey('Liquidacion', on_delete=models.CASCADE)
    salario_proporcional = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    monto_credito = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    monto_debito = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    subTotal = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, default=0)
    pago = models.ForeignKey('Pago', on_delete=models.CASCADE, null=True, blank=True, related_name='fk_liqhaber_pago')
    editable = models.BooleanField(default=True)

    class Meta:
        unique_together = (('haber', 'liquidacion'),)

    def calculo_salario_proporcional(self):

        if self.haber.movimiento.motivo.nombre != 'Contrato':
            resultado = (self.haber.movimiento.categoria_salarial.asignacion / 30) * self.liquidacion.dias_trabajados
        else:
            pago = Pago.objects.get(movimiento=self.haber.movimiento, mes=self.liquidacion.mes)
            resultado = (pago.monto / 30) * self.liquidacion.dias_trabajados
        return round(resultado)

    def suma_constante_debito(self):
        suma_monto_debito = \
        self.haber.movimiento.fk_constante_movimiento.filter(movimiento=self.haber.movimiento, tipo__tipo='D') \
            .aggregate(monto_debito=Coalesce(
            Sum(models.F('monto')), 0,
            output_field=models.DecimalField(decimal_places=2)
        ))['monto_debito'] or 0
        if self.liquidacion.tipo.nombre != 'Definitiva':
            return round(suma_monto_debito)
        else:
            return round((suma_monto_debito / 30) * self.liquidacion.dias_trabajados)

    def suma_constante_credito(self):
        suma_monto_credito = self.haber.movimiento.fk_constante_movimiento.filter(movimiento=self.haber.movimiento, tipo__tipo='C')\
            .aggregate(monto_credito=Coalesce(
                Sum(models.F('monto')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['monto_credito'] or 0
        if self.haber.movimiento.motivo.nombre != 'Contrato':
            resultado = suma_monto_credito + self.haber.movimiento.categoria_salarial.asignacion
        else:
            pago = Pago.objects.get(mes=self.liquidacion.mes, movimiento=self.haber.movimiento)
            resultado =  suma_monto_credito + pago.monto
        if self.liquidacion.tipo.nombre != 'Definitiva':
            return round(resultado)
        else:
            return round((resultado / 30) * self.liquidacion.dias_trabajados)

    def suma_credito_baja(self):
        suma_monto_credito = self.haber.movimiento.fk_constante_movimiento.filter(movimiento=self.haber.movimiento, tipo__tipo='C')\
            .aggregate(monto_credito=Coalesce(
                Sum(models.F('monto')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['monto_credito'] or 0
        return suma_monto_credito + self.salario_proporcional

    def suma_detalles_debito(self):
        suma_detalle_debito = self.detalleliquidacion_set.filter(liquidacion_haber=self.id, variable__tipo='D')\
            .aggregate(monto_debito=Coalesce(
                Sum(models.F('total_detalle')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['monto_debito'] or 0
        return suma_detalle_debito

    def suma_detalles_credito(self):
        suma_detalle_credito = self.detalleliquidacion_set.filter(liquidacion_haber=self.id, variable__tipo='C')\
            .aggregate(monto_credito=Coalesce(
                Sum(models.F('total_detalle')), 0,
                output_field=models.DecimalField(decimal_places=2)
            ))['monto_credito'] or 0
        return suma_detalle_credito

    def calcular_total(self):
        total = round((self.monto_credito) - self.monto_debito, 0)
        return total


class LiquidacionMotivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, validators=[validar_nombre], unique=True, default='Mensual')

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Motivos de Liquidacion"

    def __str__(self):
        return '%s ' % (self.nombre)


class LiquidacionType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Liquidacion"

    def __str__(self):
        return '%s ' % (self.nombre)


class DetalleLiquidacion(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, default=1, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=1, default=0, blank=True)
    total_detalle = models.DecimalField(max_digits=10, decimal_places=1, default=0, blank=True, null=True)
    #-----------------------------------Relationships-----------------------------------------#
    parametro = models.ForeignKey('Parametro', on_delete=models.CASCADE, related_name='fk_detalle_funcionario')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='fk_detalle_variable')
    constante = models.ForeignKey('Constante', on_delete=models.DO_NOTHING, blank=True, null=True)
    liquidacion_haber = models.ForeignKey('Liquidacionhaber', on_delete=models.CASCADE, db_column='liquidacion_haber_id')

    class Meta:
        unique_together = (('liquidacion_haber', 'variable'),)

    def calcular_monto(self):
        if self.monto == 0 :
            if self.liquidacion_haber.haber.movimiento.motivo.nombre != 'Contrato':
                monto = round(self.liquidacion_haber.haber.movimiento.categoria_salarial.asignacion / self.parametro.valor_numerico, 0)
            else:
                pago = Pago.objects.get(movimiento=self.liquidacion_haber.haber.movimiento, mes=self.liquidacion_haber.liquidacion.mes)
                monto = round(pago.monto / self.parametro.valor_numerico, 0)
        else:
            monto = self.monto
        return monto

    def calcular_monto_constante(self):
        if self.monto == 0 :
            monto = round(self.liquidacion_haber.subTotal * (self.constante.tipo.porcentaje / 100 ), 0)
        else:
            monto = self.monto
        return monto

    def calcular_monto_baja(self):
        if self.monto == 0 :
            monto = round(self.liquidacion_haber.salario_proporcional / self.parametro.valor_numerico, 0)
        else:
            monto = self.monto
        return monto

    def  calculo_totaldetalle(self):
        total = round(self.cantidad * self.monto, 0)
        return total


class Variable(models.Model):
    id = models.AutoField(primary_key=True)
    motivo = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    tipo = models.CharField(max_length=1, choices=ConstanteType_OPTIONS)

    class Meta:
        ordering = ["motivo"]
        verbose_name_plural = "Variables"

    def __str__(self):
        return '%s ' % (self.motivo)


class Parametro(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, default='', unique=True, null=True)
    descripcion = models.CharField(max_length=50, default='', unique=True)
    valor_numerico = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True, default=0)

    class Meta:
        ordering = ["descripcion"]
        verbose_name_plural = "Parametros"

    def __str__(self):
        return '%s ' % (self.descripcion)


class Haber(models.Model):
    id_haber = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, blank=True, default='')
    estado = models.ForeignKey('State', on_delete=models.DO_NOTHING, default=1)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE)


class Process(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DefaultProcess(models.Model):
    entity = models.CharField(max_length=20)
    process = models.ForeignKey('Process', on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.entity, self.process)


class StateType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class State(models.Model):
    stateType = models.ForeignKey('StateType', on_delete=models.CASCADE)
    process = models.ForeignKey('Process', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, default='')
    condition = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Transition(models.Model):
    process = models.ForeignKey('Process', on_delete=models.CASCADE)
    currentState = models.ForeignKey('State', on_delete=models.CASCADE, related_name='currentState')
    nextState = models.ForeignKey('State', on_delete=models.CASCADE, related_name='nextState')
    actions = models.ManyToManyField('Action', through='Transitionaction', through_fields=('transition', 'action'))
    # activities = models.ManyToManyField(Activity, related_name='activities')
    condition = models.TextField(blank=True, default='')

    def __str__(self):
        return '{} -> {}'.format(self.currentState, self.nextState)


class Action(models.Model):
    actionType = models.ForeignKey('ActionType', on_delete=models.CASCADE)
    process = models.ForeignKey('Process', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, default='')
    # showTo = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class ActionType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Transitionaction(models.Model):
    id = models.AutoField(primary_key=True)
    transition = models.ForeignKey('Transition', on_delete=models.DO_NOTHING)
    action = models.ForeignKey('Action', on_delete=models.DO_NOTHING)


class LiquidacionAction(models.Model):
    liquidacion = models.ForeignKey('Liquidacion', on_delete=models.CASCADE)
    action = models.ForeignKey('Action', on_delete=models.CASCADE)
    transition = models.ForeignKey('Transition', on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    isComplete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)
    by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Operation(models.Model):
    created_on = models.DateTimeField(null=True, blank=True)
    action = models.ForeignKey('Action', on_delete=models.CASCADE)
    transition = models.ForeignKey('Transition', on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    isComplete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)
    by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


