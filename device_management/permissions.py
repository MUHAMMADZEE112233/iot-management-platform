from rest_framework import permissions


class IsLO(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['LO', 'LE', 'LM', 'OW']


class IsLE(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['LE', 'LM', 'OW']


class IsLM(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['LM', 'OW']


class IsOW(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['OW']
