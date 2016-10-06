from datetime import timedelta

from django.db.models import Q
from haystack.forms import SearchForm
from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from haystack.query import SearchQuerySet
from django.conf import settings
from django.utils import timezone

from apps.api.models import Group, User
from apps.api.v1.account.serializers import UserPublicOnlySerializer
from apps.api.v1.rest.utils import list_dedup


# Create your views here.
from apps.api.v1.relationship.serializers import GroupSerializer


@api_view(('GET',))
def search_root(request, format=None):
    return Response({
        'search users': reverse('v1:user-search-list', request=request,
                                format=format),
        'search groups': reverse('v1:group-search-list', request=request,
                                 format=format),
    })


class SearchResultList(generics.ListAPIView):
    """
    List results of search given any queryset limited to a specific model.
    
    This class is required to be subclassed and provided with the following
    properties:
    * model
    * serializer_class
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of user objects and group objects,
    each only containing public user data.
         
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        query = ''
        results = []

        if self.request.QUERY_PARAMS.get('q'):
            # limit searchqueryset to appropriate model
            searchqueryset = SearchQuerySet().models(self.model)
            # then perform a search on specific model.
            form = SearchForm(self.request.QUERY_PARAMS,
                              searchqueryset=searchqueryset, load_all=True)
            if form.is_valid():
                query = form.cleaned_data['q']
                results = form.search()
                results = self.filter_results(results)
                # for odd reasons there are duplicates in the haystack results.
                results = list_dedup([r.object for r in results])

        return results

    def filter_results(self, results):
        """
        Filter the serch results appropriate. 
        This default implementation does nothing but return the argument.
        
        Arguments:
        - results: SearchQuerySet which contains the results of a search query
        """
        return results


class UserSearchResultList(SearchResultList):
    """
    List results of search on users
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of user objects containing only
    public data.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """

    model = User
    serializer_class = UserPublicOnlySerializer

    def get_queryset(self):
        key = self.request.GET.get('q', '')
        return User.objects.filter(Q(username__contains=key) | Q(moment__contains=key) | Q(name__contains=key)).all()

    def get_paginate_by(self):
        """
        Return all fields the user have.
        If there are no objects use the default paginate_by.
        """
        count = self.get_queryset().count()
        return count if (count > 0) else self.paginate_by


class GroupSearchResultList(SearchResultList):
    """
    List results of search on groups
    
    ## Reading
    ### Permissions
    * Anyone can read this endpoint.
    
    ### Fields
    Parameter    | Description                         | Type
    ------------ | ----------------------------------- | ----------
    `q`          | A UTF-8, URL-encoded search query   | _string_
    
    ### Response
    Reading this endpoint returns an array of group objects containing only
    public data.
             
    
    ## Publishing
    You can't write using this endpoint
    
    
    ## Deleting
    You can't delete using this endpoint
    
    
    ## Updating
    You can't update using this endpoint
    
    """

    model = Group
    serializer_class = GroupSerializer

    def filter_results(self, results):
        """
        Filter search results to exclude expired groups
        """
        earliest_date = timezone.now() - timedelta(
            seconds=settings.GROUP_EXPIRY_TIME_SECONDS)
        return results.filter(ctime__gte=earliest_date)
