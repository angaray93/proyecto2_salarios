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


class Categoria_Salarial(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    # -----------------------------------Relationships-----------------------------------------#
    jefe = models.OneToOneField('Funcionario', models.DO_NOTHING, on_delete=models.CASCADE)
    departamento = models.OneToOneField('Departamento', models.DO_NOTHING, on_delete=models.CASCADE)