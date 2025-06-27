from django.core.management.base import BaseCommand
from applications.security.models import Menu, Module, GroupModulePermission, User
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Initialize database with default data'

    def handle(self, *args, **kwargs):
        initialize_database()

def initialize_database():
    """
    Initialize the database with default data for the application.
    This includes menus, modules, users, groups, and permissions.
    """
    
    # Clear existing data (optional - use with caution)
    # GroupModulePermission.objects.all().delete()
    # Module.objects.all().delete()
    # Menu.objects.all().delete()
    # Group.objects.all().delete()
    # User.objects.all().delete()
    
    # Create Menus
    menus_data = [
        {'name': 'Pacientes', 'icon': 'bi bi-person', 'order': 1},
        {'name': 'Consultas', 'icon': 'bi bi-calendar-check', 'order': 2},
        {'name': 'Administración', 'icon': 'bi bi-gear', 'order': 4},
    ]
    
    created_menus = {}
    for menu_data in menus_data:
        menu, created = Menu.objects.get_or_create(
            name=menu_data['name'],
            defaults={'icon': menu_data['icon'], 'order': menu_data['order']}
        )
        created_menus[menu.name] = menu
    
    # Create Modules
    modules_data = [
        # Modules for Pacientes menu
        {'url': 'pacientes/', 'name': 'Registro de Pacientes', 'menu': 'Pacientes',
         'description': 'Gestión de información de pacientes', 'icon': 'bi bi-person-plus', 'order': 1},
        {'url': 'historial/', 'name': 'Historial Médico', 'menu': 'Pacientes', 
         'description': 'Historial clínico de pacientes', 'icon': 'bi bi-file-medical', 'order': 2},
        {'url': 'seguimiento/', 'name': 'Seguimiento', 'menu': 'Pacientes', 
         'description': 'Seguimiento de tratamientos y evolución', 'icon': 'bi bi-graph-up', 'order': 3},
        
        # Modules for Consultas menu
        {'url': 'citas/', 'name': 'Citas', 'menu': 'Consultas', 
         'description': 'Programación de citas médicas', 'icon': 'bi bi-calendar-date', 'order': 1},
        {'url': 'diagnosticos/', 'name': 'Diagnósticos', 'menu': 'Consultas', 
         'description': 'Registro de diagnósticos médicos', 'icon': 'bi bi-clipboard-pulse', 'order': 2},
        {'url': 'recetas/', 'name': 'Recetas', 'menu': 'Consultas', 
         'description': 'Emisión de recetas médicas', 'icon': 'bi bi-file-earmark-text', 'order': 3},
        
        # Modules for Administración menu
        {'url': 'usuarios/', 'name': 'Usuarios', 'menu': 'Administración', 
         'description': 'Gestión de usuarios del sistema', 'icon': 'bi bi-people', 'order': 1},
        {'url': 'configuracion/', 'name': 'Configuración', 'menu': 'Administración', 
         'description': 'Configuración general del sistema', 'icon': 'bi bi-sliders', 'order': 2},
        {'url': 'reportes/', 'name': 'Reportes', 'menu': 'Administración', 
         'description': 'Generación de reportes y estadísticas', 'icon': 'bi bi-bar-chart', 'order': 3}
    ]
    
    created_modules = {}
    for module_data in modules_data:
        menu = created_menus.get(module_data['menu'])
        if menu:
            module, created = Module.objects.get_or_create(
                url=module_data['url'],
                defaults={
                    'name': module_data['name'],
                    'menu': menu,
                    'description': module_data['description'],
                    'icon': module_data['icon'],
                    'order': module_data['order']
                }
            )
            created_modules[module.name] = module
    
    # Create Users
    users_data = [
        {'username': 'drgomez', 'email': 'drgomez@clinica.med', 'password': 'secure123!',
         'first_name': 'Carlos', 'last_name': 'Gómez', 'dni': '0912345678',
         'direction': 'Av. Principal 123, Guayaquil', 'phone': '0991234567', 'is_staff': True},
        
        {'username': 'asistente', 'email': 'asistente@clinica.med', 'password': 'asist2025!',
         'first_name': 'María', 'last_name': 'Sánchez', 'dni': '0923456789',
         'direction': 'Calle Secundaria 456, Guayaquil', 'phone': '0982345678', 'is_staff': False}
    ]
    
    created_users = {}
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'dni': user_data['dni'],
                'direction': user_data['direction'],
                'phone': user_data['phone'],
                'is_staff': user_data['is_staff']
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
        created_users[user.username] = user
    
    # Create Groups
    groups_data = [
        {'name': 'Médicos'},
        {'name': 'Asistentes'}
    ]
    
    created_groups = {}
    for group_data in groups_data:
        group, created = Group.objects.get_or_create(name=group_data['name'])
        created_groups[group.name] = group
    
    # Add users to groups
    if 'drgomez' in created_users and 'Médicos' in created_groups:
        created_users['drgomez'].groups.add(created_groups['Médicos'])
    
    if 'asistente' in created_users and 'Asistentes' in created_groups:
        created_users['asistente'].groups.add(created_groups['Asistentes'])
    
    # Create permissions for Patient and Diagnosis models
    try:
        patient_ct = ContentType.objects.get(app_label='doctor', model='patient')
        diagnosis_ct = ContentType.objects.get(app_label='doctor', model='diagnosis')
        
        # Patient permissions
        patient_view = Permission.objects.get_or_create(
            codename='view_patient', 
            name='Can view Paciente', 
            content_type=patient_ct
        )[0]
        patient_add = Permission.objects.get_or_create(
            codename='add_patient', 
            name='Can add Paciente', 
            content_type=patient_ct
        )[0]
        patient_change = Permission.objects.get_or_create(
            codename='change_patient', 
            name='Can change Paciente', 
            content_type=patient_ct
        )[0]
        patient_delete = Permission.objects.get_or_create(
            codename='delete_patient', 
            name='Can delete Paciente', 
            content_type=patient_ct
        )[0]
        
        # Diagnosis permissions
        diagnosis_view = Permission.objects.get_or_create(
            codename='view_diagnosis', 
            name='Can view Diagnóstico', 
            content_type=diagnosis_ct
        )[0]
        diagnosis_add = Permission.objects.get_or_create(
            codename='add_diagnosis', 
            name='Can add Diagnóstico', 
            content_type=diagnosis_ct
        )[0]
        diagnosis_change = Permission.objects.get_or_create(
            codename='change_diagnosis', 
            name='Can change Diagnóstico', 
            content_type=diagnosis_ct
        )[0]
        diagnosis_delete = Permission.objects.get_or_create(
            codename='delete_diagnosis', 
            name='Can delete Diagnóstico', 
            content_type=diagnosis_ct
        )[0]
        
        # Add permissions to modules
        if 'Registro de Pacientes' in created_modules:
            created_modules['Registro de Pacientes'].permissions.add(
                patient_view, patient_add, patient_change, patient_delete
            )
        
        if 'Diagnósticos' in created_modules:
            created_modules['Diagnósticos'].permissions.add(
                diagnosis_view, diagnosis_add, diagnosis_change, diagnosis_delete
            )
        
        # Create GroupModulePermission records
        # For Médicos with Patient module
        if 'Médicos' in created_groups and 'Registro de Pacientes' in created_modules:
            gmp1, _ = GroupModulePermission.objects.get_or_create(
                group=created_groups['Médicos'],
                module=created_modules['Registro de Pacientes']
            )
            gmp1.permissions.add(patient_view, patient_add, patient_change, patient_delete)
        
        # For Médicos with Diagnosis module
        if 'Médicos' in created_groups and 'Diagnósticos' in created_modules:
            gmp2, _ = GroupModulePermission.objects.get_or_create(
                group=created_groups['Médicos'],
                module=created_modules['Diagnósticos']
            )
            gmp2.permissions.add(diagnosis_view, diagnosis_add, diagnosis_change)
        
        # For Asistentes with Patient module (limited permissions)
        if 'Asistentes' in created_groups and 'Registro de Pacientes' in created_modules:
            gmp3, _ = GroupModulePermission.objects.get_or_create(
                group=created_groups['Asistentes'],
                module=created_modules['Registro de Pacientes']
            )
            gmp3.permissions.add(patient_view, patient_add)
        
        # For Asistentes with Diagnosis module (view only)
        if 'Asistentes' in created_groups and 'Diagnósticos' in created_modules:
            gmp4, _ = GroupModulePermission.objects.get_or_create(
                group=created_groups['Asistentes'],
                module=created_modules['Diagnósticos']
            )
            gmp4.permissions.add(diagnosis_view)
            
    except ContentType.DoesNotExist:
        print("Warning: ContentTypes for doctor.patient or doctor.diagnosis not found. Permissions not created.")
    
    print("Database initialization completed successfully.")
