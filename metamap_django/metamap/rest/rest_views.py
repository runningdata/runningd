from metamap.rest.serializers import ETLSerializer, SqoopHive2MysqlSerializer, SqoopMysql2HiveSerializer, \
    SourceAppSerializer, \
    JarAppSerializer, BIUserSerializer, AnaETLSerializer, MetaSerializer
from metamap.models import ETL, SqoopHive2Mysql, SqoopMysql2Hive, SourceApp, \
    JarApp, BIUser, AnaETL, Meta
from rest_framework import viewsets


class ETLViewSet(viewsets.ModelViewSet):
    queryset = ETL.objects.filter(valid=1).order_by('-ctime')
    serializer_class = ETLSerializer


class SourceAppViewSet(viewsets.ModelViewSet):
    queryset = SourceApp.objects.order_by('-ctime')
    serializer_class = SourceAppSerializer


class JarAppViewSet(viewsets.ModelViewSet):
    queryset = JarApp.objects.order_by('-ctime')
    serializer_class = JarAppSerializer


class SqoopHive2MysqlViewSet(viewsets.ModelViewSet):
    queryset = SqoopHive2Mysql.objects.order_by('-ctime')
    serializer_class = SqoopHive2MysqlSerializer


class SqoopMysql2HiveViewSet(viewsets.ModelViewSet):
    queryset = SqoopMysql2Hive.objects.order_by('-ctime')
    serializer_class = SqoopMysql2HiveSerializer


class SqoopHiveMetaViewSet(viewsets.ModelViewSet):
    queryset = Meta.objects.filter(type=2).order_by('-ctime')
    serializer_class = MetaSerializer


class SqoopMysqlMetaViewSet(viewsets.ModelViewSet):
    queryset = Meta.objects.filter(type=1).order_by('-ctime')
    serializer_class = MetaSerializer


class BIUserViewSet(viewsets.ModelViewSet):
    queryset = BIUser.objects.using('ykx_wd').all()
    serializer_class = BIUserSerializer


class AnaETLViewSet(viewsets.ModelViewSet):
    queryset = AnaETL.objects.filter(valid=1).order_by('-ctime')
    serializer_class = AnaETLSerializer
