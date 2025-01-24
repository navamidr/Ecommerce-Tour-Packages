from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser

class IsAgent(BasePermission):

    def has_permission(self, request, view):
        if request.user.role == CustomUser.Roles.AGENT:
            return True
        raise PermissionDenied(detail="Only agents are allowed to perform this action.")
        

class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        raise PermissionDenied(detail="You can only perform this action on your own packages.")
        
    
class IsUser(BasePermission):
    
    def has_permission(self, request, view):
        if request.user.role == CustomUser.Roles.USER:
            return True
        raise PermissionDenied(detail="only users are allowed to perform this action.")
        
        
    