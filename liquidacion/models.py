from django.db import models
from django.contrib.auth.models import User

class Funcionario(models.Model):
    idFuncionario = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=50, default='')
    nombres = models.CharField(max_length=50, default='')
    apellidos = models.CharField(max_length=50, default='')
    fechanacimiento = models.DateField()
    direccion = models.CharField(max_length=100, default='')
    email = models.CharField(max_length=50, default='')
    telefono = models.CharField(max_length=50, default='')
    cantHijos = models.IntegerField()
    #-----------------------------------Relationships-----------------------------------------#
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='fk_funcionario_usuario')
    grado = models.ForeignKey('GradoUniversitario', on_delete=models.CASCADE, related_name='fk_funcionario_usuario' )
    estadocivil = models.ForeignKey('EstadoCivil', on_delete=models.CASCADE, related_name='fk_funcionario_gradouniversitario')
    ciudadnacimiento = models.ForeignKey('Ciudad', on_delete=models.CASCADE, related_name='fk_funcionario_ciudad')
    vacaciones = models.ForeignKey('Vacaciones', on_delete=models.CASCADE, related_name='fk_funcionario_vacaciones')

    class Meta:
        ordering = ["apellidos"]
        verbose_name_plural = "Funcionarios"

    def __str__(self):
        return '%s %s' % (self.nombres, self.apellidos)


class Movimiento(models.Model):
    idmovimiento = models.AutoField(primary_key=True)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    esPrimero = models.BooleanField(default=True)
    horaEntrada = models.TimeField()
    horaSalida = models.TimeField()
    tieneAguinaldo = models.BooleanField(default=False)
    tieneVacaciones = models.BooleanField(default=False)
    tieneSeguroMedico = models.BooleanField(default=False)
    #-----------------------------------Relationships-----------------------------------------#
    documentorespaldatorio = models.ForeignKey('DocumentoRespaldatorio', on_delete=models.CASCADE, related_name='fk_movimiento_documentorespaldatorio')
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_movimiento_funcionario')
    categoria_salarial = models.ForeignKey('CategoriaSalarial', on_delete=models.CASCADE, related_name='fk_movimiento_categoriasalarial')
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE, related_name='fk_movimiento_departamento')
    og = models.ForeignKey('Objeto_De_Gasto', on_delete=models.CASCADE, related_name='fk_movimiento_og')
    motivo = models.ForeignKey('MovimientoMotivo', on_delete=models.CASCADE, related_name='fk_movimiento_motivo')
    tipo = models.ForeignKey('MovimientoType', on_delete=models.CASCADE, related_name='fk_movimiento_tipo')


class Objeto_De_Gasto(models.Model):
    id_og = models.AutoField(primary_key=True)
    concepto = models.CharField(max_length=100, default='')
    numero = models.IntegerField()


class Departamento(models.Model):
    iddepartamento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    director = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_departamento_funcionario')


class Division(models.Model):
    iddivision = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    jefe = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_division_funcionario')
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE, related_name='fk_division_departamento')


class Aguinaldo(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad_meses = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.ForeignKey('Movimiento', on_delete=models.CASCADE, related_name='fk_aguinaldo_movimiento')


class Pais(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class Ciudad(models.Model):
    idciudad = models.AutoField(primary_key=True)
    nombreciudad = models.CharField(max_length=50, default='')
    # -----------------------------------Relationships-----------------------------------------#
    pais = models.ForeignKey('Pais', on_delete=models.CASCADE, related_name='fk_ciudad_pais')


class CategoriaSalarial(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, default='')
    tipo = models.CharField(max_length=30, default='')
    cargo = models.CharField(max_length=50, default='')
    asignacion = models.IntegerField()

    class Meta:
        ordering = ["codigo"]
        verbose_name_plural = "Categorias Salariales"

    def __str__(self):
        return '%s ' % self.codigo


class EstadoCivil(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class GradoUniversitario(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class Vacaciones(models.Model):
    id = models.AutoField(primary_key=True)
    inicio = models.DateField()
    fin = models.DateField()
    cantidadmeses = models.DecimalField(max_digits=10, decimal_places=2)
    cantidaddias = models.IntegerField()
    monto = models.DecimalField(max_digits=20, decimal_places=2,)
    # -----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name= 'fk_vacaciones_funcionario')


class Constante(models.Model):
    id = models.AutoField(primary_key=True)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    monto = models.IntegerField()
    # -----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_constante_funcionario')
    tipo = models.ForeignKey('ConstanteType', on_delete=models.CASCADE, related_name='fk_constante_tipo')


class ConstanteType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')
    tipo = models.CharField(max_length=1, default='')


class MovimientoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class MovimientoMotivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class DocumentoRespaldatorio(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, default='')
    fechaemision = models.DateField()
    quienfirma = models.CharField(max_length=50, default='')
    # -----------------------------------Relationships-----------------------------------------#
    tipo = models.ForeignKey('DocumentoType', on_delete=models.CASCADE, related_name='fk_documentorespaldatorio_tipo')
    autoridadfirmante = models.ForeignKey('AutoridadFirmante', on_delete=models.CASCADE, related_name='fk_documentorespaldatorio_autoridadfirmante')


class DocumentoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, default='')


class AutoridadFirmante(models.Model):
    id = models.AutoField(primary_key=True)
    cargo = models.CharField(max_length=50, blank=True, default='')


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
    nombre = models.CharField(max_length=50, default='')


class DetalleLiquidacion(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    #-----------------------------------Relationships-----------------------------------------#
    parametro = models.ForeignKey('Funcionario', on_delete=models.CASCADE, related_name='fk_detalle_funcionario')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='fk_detalle_variable')
    liquidacion = models.ForeignKey('State', on_delete=models.CASCADE, related_name='fk_detalle_liquidacion')


class Variable(models.Model):
    id = models.AutoField(primary_key=True)
    motivo = models.CharField(max_length=50, blank=True, default='')
    tipo = models.CharField(max_length=1, blank=True, default='')


class Parametro(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, blank=True, default='')
    descripcion = models.CharField(max_length=50, blank=True, default='')


class Haber(models.Model):
    id_haber = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    movimiento = models.OneToOneField('Movimiento', on_delete=models.CASCADE)


class Liquidacionhaber(models.Model):
    id = models.AutoField(primary_key=True)
    haber = models.ForeignKey(Haber, on_delete=models.CASCADE)
    liquidacion = models.ForeignKey('Liquidacion', on_delete=models.CASCADE)


class State(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    tipo = models.ForeignKey('StateType', on_delete=models.CASCADE)


class StateType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
