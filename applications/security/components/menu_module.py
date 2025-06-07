from datetime import datetime
from django.contrib.auth.models import Group
from django.http import HttpRequest

from applications.security.models import GroupModulePermission, User
from applications.security.models import Module, Menu


class MenuModule:
    def __init__(self, request: HttpRequest):
        self._request = request
        self._path = self._request.path

    def fill(self, data):
        """Llena el contexto con datos de usuario, grupo y menús."""
        try:
            data['user'] = self._request.user
            data['date_time'] = datetime.now()
            data['date_date'] = datetime.now().date()

            if not self._request.user.is_authenticated:
                return

            if self._request.method != 'GET':
                return

            data['group_list'] =self._request.user.groups.all().order_by('id')

            if self._request.user.is_superuser:
                data['menu_list'] = self.__get_superuser_menu_list()
                return

            # Lógica normal basada en grupo
            if 'group_id' not in self._request.session:
                if data['group_list'].exists():
                    self._request.session['group_id'] = data['group_list'].first().id

            group_id = self._request.GET.get('gpid')
            if group_id:
                try:
                    self._request.session['group_id'] = int(group_id)
                except (ValueError, TypeError):
                    pass  # Si es inválido, ignoramos

            if self._request.session.get('group_id'):
                try:
                    group = Group.objects.get(id=self._request.session['group_id'])
                    data['group'] = group

                    data['menu_list'] = self.__get_menu_list(data["user"], group)
                    
                except Group.DoesNotExist:
                    data['menu_list'] = []
        except Exception as ex:
            print(f"[ERROR] Error al llenar menú: {ex}")
            data['menu_list'] = []

    def __get_menu_list(self, user: User, group: Group):
        """Obtiene los módulos asociados a un grupo."""
        try:
            group_module_permission_list = (
                GroupModulePermission.objects
                .select_related('module', 'module__menu')
                .filter(
                    group=group,
                    module__is_active=True
                )
                .order_by('module__menu__order', 'module__order')
            )

            # Extender cada módulo con sus permisos sin modificar el objeto real
            extended_modules = []
            for item in group_module_permission_list:
                extended_modules.append({
                    'module': item.module,
                    'permissions': list(item.permissions.all())  # Guardamos los permisos como lista
                })

            menu_ids = group_module_permission_list.values_list('module__menu_id', flat=True).distinct()
            menus = Menu.objects.filter(id__in=menu_ids).order_by('order')

            menu_list = [
                self._get_data_menu_list(menu, extended_modules)
                for menu in menus
            ]
   
            return menu_list

        except Exception as ex:
            print(f"[ERROR] __get_menu_list: {ex}")
            return []


    def _get_data_menu_list(self, menu: Menu, extended_modules):
        """Construye un menú con sus submenús/módulos y sus permisos."""
        try:
            # Filtramos los módulos extendidos que pertenecen a este menú
            filtered = [m for m in extended_modules if m['module'].menu_id == menu.id]

            return {
                'menu': menu,
                'group_module_permission_list': filtered
            }
        except Exception as ex:
            print(f"[ERROR] _get_data_menu_list: {ex}")
            return {'menu': None, 'group_module_permission_list': []}
        

    def __get_superuser_menu_list(self):
        """Obtiene todos los módulos y menús del sistema para superusuario."""
        try:
            # Obtener todos los módulos activos
            all_modules = Module.objects.filter(is_active=True).order_by('menu__order', 'order')
                  # Obtener todos los menús asociados a esos módulos
            menus = Menu.objects.filter(modules__in=all_modules).distinct().order_by('order')
          
            menu_list = []

            for menu in menus:
                modules_in_menu = all_modules.filter(menu=menu)

                module_permissions = []
                for module in modules_in_menu:
                    # Simulamos un objeto similar a GroupModulePermission
                    fake_group_module = type('FakeGroupModule', (), {})()
                    fake_group_module.module = module
                    fake_group_module.permissions = module.permissions.all()  # Permisos reales del módulo

                    module_permissions.append(fake_group_module)

                menu_list.append({
                    'menu': menu,
                    'group_module_permission_list': module_permissions,
                })

            return menu_list

        except Exception as ex:
            print(f"[ERROR] __get_superuser_menu_list: {ex}")
            return []
          