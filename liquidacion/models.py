import datetime

from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    usuario = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='fk_funcionario_usuario')
    grado = models.ForeignKey('GradoUniversitario', on_delete=models.DO_NOTHING, related_name='fk_funcionario_usuario' )
    estadocivil = models.ForeignKey('EstadoCivil', on_delete=models.DO_NOTHING, related_name='fk_funcionario_gradouniversitario', verbose_name='Estado Civil')
    ciudadnacimiento = models.ForeignKey('Ciudad', on_delete=models.DO_NOTHING, related_name='fk_funcionario_ciudad', verbose_name='Lugar de Nacimiento')

    class Meta:
        ordering = ["apellidos"]
        verbose_name_plural = "Funcionarios"

    def __str__(self):
        return '%s %s' % (self.nombres, self.apellidos)


class Movimiento(models.Model):
    idmovimiento = models.AutoField(primary_key=True)
    tipo = models.ForeignKey('MovimientoType', on_delete=models.DO_NOTHING, related_name='fk_movimiento_tipo')
    motivo = models.ForeignKey('MovimientoMotivo', on_delete=models.DO_NOTHING, related_name='fk_movimiento_motivo')
    formapago = models.CharField(max_length=1, default='M',choices=Modalidad_OPTIONS)
    fechainicio = models.DateField()
    fechafin = models.DateField(blank=True, null=True)
    esPrimero = models.BooleanField(default=True)
    horaEntrada = models.TimeField()
    horaSalida = models.TimeField()
    tieneAguinaldo = models.BooleanField(default=False)
    tieneVacaciones = models.BooleanField(default=False)
    funcion = models.CharField(max_length=100, default='')
    #-----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', on_delete=models.DO_NOTHING, related_name='fk_movimiento_funcionario')
    categoria_salarial = models.ForeignKey('CategoriaSalarial', on_delete=models.DO_NOTHING,
                                           related_name='fk_movimiento_categoriasalarial', blank=True, null=True)
    division = models.ForeignKey('Division', on_delete=models.DO_NOTHING, related_name='fk_movimiento_division')
    og = models.ForeignKey('Objeto_De_Gasto', on_delete=models.DO_NOTHING, related_name='fk_movimiento_og')
    movimiento_padre = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True)
    estado = models.ForeignKey('State', on_delete=models.DO_NOTHING, related_name='fk_movimiento_estado')


class Pago(models.Model):
    id = models.AutoField(primary_key=True)
    mes = models.CharField(max_length=10 ,choices=MES_OPTIONS, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pagado = models.BooleanField(default=False)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='fk_pago_movimiento')


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
    cantidad_meses = models.DecimalField(default=0, max_digits=2, decimal_places=1, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.OneToOneField('Movimiento', on_delete=models.CASCADE, related_name='aguinaldo_movimiento')


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

    #def __str__(self):
    #    return '%s %s %s' % (self.nombreciudad, ' - ', self.pais)


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
    inicio = models.DateField()
    fin = models.DateField(blank=True, null=True)
    diasobtenidos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    diasusados = models.IntegerField(default=0)
    monto = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.OneToOneField('Movimiento', on_delete=models.CASCADE, related_name= 'vacaciones_movimiento')


class Constante(models.Model):
    id = models.AutoField(primary_key=True)
    finito = models.BooleanField(default=False)
    cantidad_veces = models.IntegerField(blank=True, null=True)
    ocurrencias = models.IntegerField(blank=True, null=True, default=0)
    monto = models.IntegerField(blank=True, null=True, default=0)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='fk_constante_movimiento')
    tipo = models.ForeignKey('ConstanteType', on_delete=models.CASCADE, related_name='fk_constante_tipo')

    def calcular_monto(self):
        if self.tipo.porcentaje != 0 and self.tipo.porcentaje is not None:
            return ((self.movimiento.categoria_salarial.asignacion * self.tipo.porcentaje) / Decimal(100))
        else:
            return self.monto


class ConstanteType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    tipo = models.CharField(max_length=1, choices=ConstanteType_OPTIONS)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Constante"

    def __str__(self):
        if self.porcentaje != 0 :
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
    fechacreacion = models.DateField()
    ultimamodificacion = models.DateField()
    mes = models.IntegerField()
    total_debito = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    total_credito = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    total_liquidacion = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    inicio_periodo = models.DateField()
    fin_periodo = models.DateField()
    #-----------------------------------Relationships-----------------------------------------#
    haberes = models.ManyToManyField('Haber', through='Liquidacionhaber', through_fields=('liquidacion', 'haber'))
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_liquidacion_funcionario')
    estado_actual = models.ForeignKey('State', on_delete=models.CASCADE, related_name='fk_liquidacion_estado')
    tipo = models.ForeignKey('LiquidacionType', on_delete=models.CASCADE, related_name='fk_liquidacion_tipo')
    propietario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_liquidacion_user')


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
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    #-----------------------------------Relationships-----------------------------------------#
    parametro = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_detalle_funcionario')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='fk_detalle_variable')
    liquidacion = models.ForeignKey('Liquidacion', on_delete=models.CASCADE, related_name='fk_detalle_liquidacion')


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
    codigo = models.CharField(max_length=50, default='', unique=True)
    descripcion = models.CharField(max_length=50, default='', unique=True)

    class Meta:
        ordering = ["descripcion"]
        verbose_name_plural = "Parametros"

    def __str__(self):
        return '%s ' % (self.descripcion)


class Haber(models.Model):
    id_haber = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.OneToOneField('Movimiento', on_delete=models.CASCADE)


class Liquidacionhaber(models.Model):
    id = models.AutoField(primary_key=True)
    haber = models.ForeignKey(Haber, on_delete=models.CASCADE)
    liquidacion = models.ForeignKey('Liquidacion', on_delete=models.CASCADE)


"""class State(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)
    tipo = models.ForeignKey('StateType', on_delete=models.CASCADE)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Estados de Liquidacion Salarial"

    def __str__(self):
        return '%s ' % (self.nombre)


class StateType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='', validators=[validar_nombre], unique=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "Tipos de Estado de Liquidacion"

    def __str__(self):
        return '%s ' % (self.nombre)"""


class Process(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DefaultProcess(models.Model):
    entity = models.CharField(max_length=20)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)

    def __str__(self):
        return '{} - {}'.format(self.entity, self.process)


class StateType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class State(models.Model):
    stateType = models.ForeignKey(StateType, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, default='')
    condition = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class ActionType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Action(models.Model):
    actionType = models.ForeignKey(ActionType, on_delete=models.CASCADE)
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True, default='')
    #showTo = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Transition(models.Model):
    process = models.ForeignKey(Process, on_delete=models.CASCADE)
    currentState = models.ForeignKey(State, on_delete=models.CASCADE, related_name='currentState')
    nextState = models.ForeignKey(State, on_delete=models.CASCADE, related_name='nextState')
    #actions = models.ManyToManyField(Action, db_table='KHCRM_transitionaction')
    #activities = models.ManyToManyField(Activity, related_name='activities')
    condition = models.TextField(blank=True, default='')

    def __str__(self):
        return '{} -> {}'.format(self.currentState, self.nextState)


'''class PropuestaAction(models.Model):
    propuesta = models.ForeignKey('Propuesta', on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    transition = models.ForeignKey(Transition, on_delete=models.CASCADE)
    isActive = models.BooleanField(default=True)
    isComplete = models.BooleanField(default=False)
    completed_on = models.DateTimeField(null=True, blank=True)
    by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(self.id, self.propuesta, self.action, self.transition)'''
