from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser

class IsAgent(BasePermission):

    def has_permission(self, request, view):
        if request.user.role != CustomUser.Roles.AGENT:
            raise PermissionDenied(detail="Only agents are allowed to perform this action.")
        return True
    

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner != request.user:
            raise PermissionDenied(detail="You can only perform this action on your own packages.")
        return True
    
class IsUser(BasePermission):
    
    def has_permission(self, request, view):
        if request.user.role != CustomUser.Roles.USER:
            raise PermissionDenied(detail="only users are allowed to perform this action.")
        return True
        
    