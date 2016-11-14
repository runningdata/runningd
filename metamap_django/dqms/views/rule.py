from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from dqms.models import DqmsRule
from dqms.serializers import DqmsRuleSerializer


class RuleViewSet(viewsets.ModelViewSet):
    serializer_class = DqmsRuleSerializer
    queryset = DqmsRule.objects.all()

    @list_route(methods=['GET'])
    def get_all(self, request):
        case_id = int(request.GET['id'])
        result = DqmsRule.objects.filter(case_id=case_id)
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)