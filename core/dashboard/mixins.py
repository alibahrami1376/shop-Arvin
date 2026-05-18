"""Dashboard views: separate mobile/desktop templates via DeviceTemplateMixin."""

from core.mixins import DeviceTemplateMixin

DashboardDeviceTemplateMixin = DeviceTemplateMixin

__all__ = ["DashboardDeviceTemplateMixin"]
