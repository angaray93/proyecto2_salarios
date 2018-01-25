from django.db import models

class Funcionario(models.Model):
    idFuncionario = models.AutoField(primary_key=True)
    cedula = models.CharField(max_length=500, default='')
    nombres = models.CharField(max_length=500, default='')
    apellidos = models.CharField(max_length=500, default='')
    fechanacimiento = models.DateField()
    direccion = models.CharField(max_length=500, blank=True, default='')
    email = models.CharField(max_length=500, blank=True, default='')
    telefono = models.CharField(max_length=500, blank=True, default='')
    cantHijos = models.IntegerField()
    #-----------------------------------Relationships-----------------------------------------#
    ciudad = models.ForeignKey('User', models.DO_NOTHING, on_delete=models.CASCADE)
    # grado = models.ForeignKey('GradoUniversitario', models.DO_NOTHING, on_delete=models.CASCADE)
    # estadocivil = models.ForeignKey('EstadoCivil', models.DO_NOTHING, on_delete=models.CASCADE)
    # ciudadnacimiento = models.ForeignKey('Ciudad', models.DO_NOTHING, on_delete=models.CASCADE)
    # constante
    # vacaciones


class Movimiento(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    esPrimero = models.BooleanField(default='False')
    horaEntrada = models.TimeField()
    horaSalida = models.TimeField()
    tieneAguinaldo = models.BooleanField(default='False')
    tieneVacaciones = models.BooleanField(default='False')
    tieneSeguroMedico = models.BooleanField(default='False')
    #-----------------------------------Relationships-----------------------------------------#
    # documentorespaldatorio = models.ForeignKey('DocumentoRespaldatorio', models.DO_NOTHING, on_delete=models.CASCADE)
    # funcionario = models.ForeignKey('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    # categoria_salarial = models.ForeignKey('CategoriaSalarial', models.DO_NOTHING, on_delete=models.CASCADE)
    # departamento = models.ForeignKey('Departamento', models.DO_NOTHING, on_delete=models.CASCADE)
    # og = models.ForeignKey('Objeto_De_Gasto', models.DO_NOTHING, on_delete=models.CASCADE)
    # aguinaldo = models.ForeignKey('Aguinaldo', models.DO_NOTHING, on_delete=models.CASCADE)
    # motivo = models.ForeignKey('MovimientoMotivo', models.DO_NOTHING, on_delete=models.CASCADE)
    # tipo = models.ForeignKey('MovimientoType', models.DO_NOTHING, on_delete=models.CASCADE)


class Objeto_De_Gasto(models.Model):
    id_og = models.AutoField(primary_key=True)
    concepto = models.CharField(max_length=50, blank=True, default='')
    numero = models.IntegerField()


class Departamento(models.Model):
    iddepartamento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    director = models.OneToOneField('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)


class Division(models.Model):
    iddivision = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    jefe = models.OneToOneField('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    departamento = models.OneToOneField('Departamento', models.DO_NOTHING, on_delete=models.CASCADE)


class Aguinaldo(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad_meses = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class Pais(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class Ciudad(models.Model):
    idciudad = models.AutoField(primary_key=True)
    nombreciudad = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    pais = models.ForeignKey('Pais', models.DO_NOTHING, on_delete=models.CASCADE)


class CategoriaSalarial(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, blank=True, default='')
    tipo = models.CharField(max_length=50, blank=True, default='')
    cargo = models.CharField(max_length=50, blank=True, default='')
    asignacion = models.IntegerField()


class EstadoCivil(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class GradoUniversitario(models.Model):
    idpais = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class Vacaciones(models.Model):
    id = models.AutoField(primary_key=True)
    inicio = models.DateField()
    fin = models.DateField()
    cantidadmeses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cantidaddias = models.IntegerField()
    monto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


class Constante(models.Model):
    id = models.AutoField(primary_key=True)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    monto = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    # -----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    tipo = models.ForeignKey('ConstanteType', models.DO_NOTHING, on_delete=models.CASCADE)


class ConstanteType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    tipo = models.CharField(max_length=1, blank=True, default='')


class MovimientoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class MovimientoMotivo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class DocumentoRespaldatorio(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=50, blank=True, default='')
    fechaemision = models.DateField()
    quienfirma = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    tipo = models.ForeignKey('DocumentoType', models.DO_NOTHING, on_delete=models.CASCADE)
    autoridadfirmante = models.ForeignKey('AutoridadFirmante', models.DO_NOTHING, on_delete=models.CASCADE)


class DocumentoType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')
    # -----------------------------------Relationships-----------------------------------------#
    director = models.ForeignKey('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)


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
    haberes = models.ManyToManyField('Haber', through='Liquidacionhaber', through_fields=('liquidacion', 'haber'))
    #-----------------------------------Relationships-----------------------------------------#
    funcionario = models.ForeignKey('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    estado_actual = models.ForeignKey('State', models.DO_NOTHING, on_delete=models.CASCADE)
    tipo = models.ForeignKey('LiquidacionType', models.DO_NOTHING, on_delete=models.CASCADE)
    propietario = models.ForeignKey('User', models.DO_NOTHING, on_delete=models.CASCADE)


class LiquidacionType(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, blank=True, default='')


class DetalleLiquidacion(models.Model):
    id = models.AutoField(primary_key=True)
    cantidad = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=1, blank=True, null=True)
    #-----------------------------------Relationships-----------------------------------------#
    parametro = models.ForeignKey('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    liquidacion = models.ForeignKey('State', models.DO_NOTHING, on_delete=models.CASCADE)


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
    # movimiento = models.OneToOneField('Movimiento', models.DO_NOTHING, on_delete=models.CASCADE)


class Liquidacionhaber(models.Model):
    id = models.AutoField(primary_key=True)
    haber = models.ForeignKey(Haber, on_delete=models.CASCADE)
    liquidacion = models.ForeignKey(Liquidacion, on_delete=models.CASCADE)