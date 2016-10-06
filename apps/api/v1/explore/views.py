from datetime import timedelta

from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.conf import settings
from django.utils import timezone

from apps.api.models import Group


# Create your views here.
from apps.api.v1.relationship.serializers import GroupSerializer


@api_view(('GET',))
def explore_root(request, format=None):
    return Response({
        'popular groups': reverse('v1:explore-popular-list',
                                  request=request, format=format),
    })


class PopularGroupsList(generics.ListAPIView):
    """
    List of popular groups.
        
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Reading this endpoint returns a list of [Group objects](/api/v1/groups/) 
    containing each group's public data only.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = GroupSerializer

    def get_queryset(self):
        """
        This view should return the list of all groups sorted by descending likes
        while excluding expired groups
        """
        earliest_date = timezone.now() - timedelta(
            seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        return Group.objects.all().filter(created_at__gte=earliest_date) \
            .order_by('-likes_count')
        

