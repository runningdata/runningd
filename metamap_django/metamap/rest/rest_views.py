from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.response import Response

from metamap.rest.serializers import ETLSerializer, SqoopHive2MysqlSerializer, SqoopMysql2HiveSerializer, \
    SourceAppSerializer, \
    JarAppSerializer, AnaETLSerializer, MetaSerializer, ExecObjSerializer
from metamap.models import ETL, SqoopHive2Mysql, SqoopMysql2Hive, SourceApp, \
    JarApp, AnaETL, Meta, ExecObj
from rest_framework import viewsets


class ETLViewSet(viewsets.ModelViewSet):
    queryset = ETL.objects.filter(valid=1).order_by('-ctime')
    serializer_class = ETLSerializer


class ExecObjViewSet(viewsets.ModelViewSet):
    queryset = ExecObj.objects.order_by('name')
    serializer_class = ExecObjSerializer

    @list_route(methods=['get'])
    def get_all(self, request, pk=None):
        if request.user.username == 'admin':
            deps = ExecObj.objects.all().order_by('name')
        else:
            deps = ExecObj.objects.filter(cgroup=request.user.userprofile.org_group).order_by('name')
        serializer = self.get_serializer(deps, many=True)
        return Response(serializer.data)


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


class AnaETLViewSet(viewsets.ModelViewSet):
    # queryset = AnaETL.objects.filter(valid=1).order_by('-ctime')
    queryset = ExecObj.objects.filter(type=2)
    serializer_class = AnaETLSerializer
