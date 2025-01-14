"""
Views for the recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Recipe,
    Tag,
    Ingredient,
)
from recipe import serializers

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma seperated list of tags IDs to filter',
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma seperated list of ingredients IDs to filter',
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    # it provides different enpoints like listing,detail..
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]
    
    # when resipes are returned those should be filtered down
    # to the authenticated user so going to override 
    # get_queryset method.
    def get_queryset(self):
        """Rectrieve recipes for authenticated user."""
        # return self.queryset.filter(user=self.request.user).order_by('-id')
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)    
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)    
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)
        
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()
            

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class
    
    def perform_create(self,serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    # detail=True, this action is going to apply to the detail portion
    # of our model view, detail means it is specific id of a recipe
    # upload-image custom url path for our action.
    @action(methods=['POST'], detail=True, url_path='upload_image')
    def upload_image(self, request, pk=None):
        """Upload an image to recipe."""
        # The get_object method in Django REST Framework (DRF) is a utility method provided by the ViewSet and GenericAPIView classes.
       #  It retrieves the specific object (typically a model instance) that the current view is supposed to act upon.
        recipe = self.get_object()
        # get_serializer it will indirectly run get_serializer_class
        # to get instance of the serializer class and it will return the
        # image serializer
        # passing data to serializer that we got at this endpoint.
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                # specific options for making the requests in the API documentation
                OpenApiTypes.INT, enum=[0,1],
                description='Filter by items assigned to recipes.',
            ),
        ]
    )
)   
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin, 
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            # means there is recipe associated with the value
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(
            user=self.request.user
            ).order_by('-name').distinct()

class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
   
class IngredientViewSet(BaseRecipeAttrViewSet) :
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()





