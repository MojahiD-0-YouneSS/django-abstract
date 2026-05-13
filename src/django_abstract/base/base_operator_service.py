from django_abstract.utilities import ClassInfoProvider,ServiceEntryData,ServiceDataOperator
from django.core.exceptions import ValidationError
from django_abstract.log.utilities import ErrorSuccessLogger
from django.utils import timezone

class BaseOperatorService(ClassInfoProvider):
    model_dependency=None
    model_slug = None
    last_updated = None
    hooks_list = []
    operator_class = ServiceDataOperator
    entry_class = ServiceEntryData

    def __init__(
        self,
        session_key,
        *args,
        include_session=False,
        include_session_key_as=None,
        auto_create=False,
        **db_required_fields,
    ):
        db_required_fields.update(
            (
                {
                    include_session_key_as or "session_key": session_key,
                }
                if include_session
                else {}
            )
        )
        self.include_session_key_as = include_session_key_as
        self.include_session = include_session
        self.session_key = session_key
        self.auto_create = auto_create
        self.validator = self.BaseServiceValidator
        self.__db_required_fields = db_required_fields
        super().__init__()

    def init_state_hook(self):

        self.db_record = self.read_entry(**self.__db_required_fields)

        self.entry = self.entry_class.load_obj_data(self.db_record)
        self.operator = self.operator_class(self.entry)
        self.operator.init_default_state()

    class BaseServiceValidator:
        def __init__(self,dependency, **data):
            self.MINIMUM_WRITE_FIELDS = []
            self.MINIMUM_READ_FIELDS = []
            self.SERVICE_DOMAIN_FIELDS = []
            self.METHOD_COLLECTION = {}
            self.RESERVED_DB_METHODS = {
                "read_entry":[],
                "delete_entry":[],
                "create_entry":[],
            }
            self.parent_service = None
            self.data = data
            self.dependency = dependency
            # Model fields to avoid random writing!
            self.VALID_FIELDS = {}
            self.VALID_FIELDS_PER_ACTION = {} # {method_name:[valid_fields]} to avoid random writing per action!
            self.cross_domain_data = {}
            self.is_cross_domain = False
            self.behavior = ServiceEntryData()
            self.meta_hook()
            self.run_service_check()

        def load_settings(self,settings):
            self.RESERVED_DB_METHODS = settings.RESERVED_DB_METHODS
            self.MINIMUM_WRITE_FIELDS = settings.MINIMUM_WRITE_FIELDS
            self.SERVICE_DOMAIN_FIELDS = settings.SERVICE_DOMAIN_FIELDS
            self.VALID_FIELDS = settings.VALID_FIELDS
            self.VALID_FIELDS_PER_ACTION = settings.VALID_FIELDS_PER_ACTION
            self.MINIMUM_READ_FIELDS = settings.MINIMUM_READ_FIELDS
            self.VALID_FIELDS_PER_ACTION = settings.VALID_FIELDS_PER_ACTION
            return self

        def can_run(self, *required_fields: list[str],dry_run=False, **data) -> bool:
            """Validate required fields are present and not None in data."""
            fields= required_fields if required_fields else ( self.MINIMUM_WRITE_FIELDS or self.MINIMUM_READ_FIELDS)
            raw_data = data if data else self.data
            if fields:
                for field in fields:
                    if field not in raw_data or raw_data[field] is None:
                        if not dry_run:
                            raise ValidationError(f"Missing or invalid field: {field}")
                        else:
                            return False
            return True

        def meta_hook(self):
            """Lifecycle hook: Override in subclasses to build registries before validation."""
            pass

        def parent_service_hook(self,parent_instance):
            """Lifecycle hook: Override in subclasses to build registries before validation."""

            self.parent_service=parent_instance

        def set_db_methods_fields(self,method_name, *required_fields):
            method_name = self.RESERVED_DB_METHODS.get(method_name,None)

            if method_name:
                self.RESERVED_DB_METHODS[method_name]=list(required_fields)            

        def run_service_check(self,*required_fields, **data):

            raw_data = (data or self.data)

            method_name = raw_data.get("method_name")
            if method_name:
                if method_name in self.RESERVED_DB_METHODS:
                    method_required_fields = self.RESERVED_DB_METHODS.get(method_name, [])
                else:
                    method_required_fields = self.VALID_FIELDS_PER_ACTION.get(method_name, [])
                check = self.can_run(
                    *method_required_fields,
                    **{ k:v for k,v in raw_data.items() if k != "method_name" },
                )

            else:
                check = self.can_run(
                    *required_fields,
                    **raw_data,
                )

            if check:
                for field in self.SERVICE_DOMAIN_FIELDS:
                    if field in raw_data:
                        self.VALID_FIELDS[field]=raw_data[field]
                return self.VALID_FIELDS

            return {}

        def regester_method(self,name,method):
            self.METHOD_COLLECTION[name]=method
            return self

        def get_method_args(self, method_name):
            valid_fields = self.VALID_FIELDS_PER_ACTION.get(method_name, [])
            valid_domain_fields = self.run_service_check(*valid_fields,)
            if self.is_cross_domain:
                return [valid_domain_fields.get(field) for field in self.cross_domain_data.keys() if field in valid_domain_fields]
            return list(valid_domain_fields.values())

        def run(self, method_name,):
            if not method_name:
                return False
            if not self.METHOD_COLLECTION:
                return False

            method =  self.METHOD_COLLECTION.get(method_name,None)
            if method:
                method()
                return True
            return False

    def hook(self, entry=None,):
        entry = entry or self.entry
        if self.can_run(**entry.service_data):
            return self.run_skeleten(**entry.service_data)
        return None

    def hook_pad(
        self,
        *hook_names: str,
        entry: ServiceEntryData | None = None,
        service_type: str | None = None,
    ):
        service_type = service_type or 'MODEL_SERVICE'
        if hook_name and not hook_name in self.hooks_list:
            return False
        if hook_name:
            from django_abstract.registry import SERVICE_REGISTRY
            for hook_name in hook_names:
                target_service = SERVICE_REGISTRY[service_type].get(hook_name)
                if target_service and hasattr(target_service, 'hook'):
                    target_service.hook(obj=entry or self.entry)
        else:
            for hook in self.hooks_list:
                target_service = SERVICE_REGISTRY['MODEL_SERVICE'].get(hook)
                if not target_service:
                    target_service = SERVICE_REGISTRY['BARE_SERVICE'].get(hook)
                if target_service and hasattr(target_service, 'hook'):
                    target_service.hook(obj=entry or self.entry, )
            return True

    def run_skeleten(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """
        validator  = self.validator(dependency=self.model_dependency,**kwargs)
        validator.run(
            method_name=self.entry.service_data.get('method_name'),
        )
        self.entry.service_data = validator.behavior.service_data
        if self.is_exists(**kwargs):
            if not self.operator.should_update():
                return self.entry

            self.operator.pending_updates.update(kwargs)
            self.last_updated = timezone.now()

            # Only save every 5 seconds or when explicitly flushed
            if (self.last_updated - getattr(self, '_last_save', timezone.now())).seconds >= 5:
                self.operator.flush_updates(pending_updates=self.operator.pending_updates)
                self.db_record.bulk_update(self.entry.service_data)
                self.db_record.save()
            self.entry.load_obj_data(self.db_record)
            return self.entry
        self.entry.errors['record_exists']=False
        return self.entry

    def read_entry(self, **kwargs):

        kwargs["method_name"]="read_entry"
        validator = self.validator(self.model_dependency,**kwargs)
        validator.parent_service_hook(self)
        data = validator.run_service_check()        
        try:
            if self.is_exists(**data):

                return self.access_db_objects.get(**data)
            else:
                return self.create_entry(**data) if self.auto_create else None

        except Exception as e:
            self.logging_hook(operation=f'RETRIEVING {self.session_key.upper()}' , e=e, **kwargs)
            raise e

    def logging_hook(self, operation, e=None, **kwargs):
        """Logs the operation and error message"""
        error_message = f' Failed {operation.lower()} of user {self.session_key} with data {kwargs}. trace back: {e} '
        operation += f' OF USER {self.session_key}'
        return ErrorSuccessLogger().logging_check(operation=operation, service_data=self.get_class_info(), error_message=error_message)

    def is_exists(self,  **kwargs):
        data = self.validator(self.model_dependency,**kwargs).run_service_check()
        return self.access_db_objects.filter(**data).exists()

    def can_run(self,method_name, **kwargs) -> bool:
        validator =  self.validator(self.model_dependency,**kwargs)
        required_fields = validator.VALID_FIELDS_PER_ACTION.get(method_name)
        flag = validator.can_run(*required_fields,)
        return flag

    def delete_entry(self,):
        return self.access_db_objects.delete(id=self.entry.obj_id)

    def create_entry(self,**kwargs):
        validator = self.validator(self.model_dependency, **kwargs)
        validator.parent_service_hook(self)
        data = validator.run_service_check()
        if data:
            return self.access_db_objects.create(**data)
        else:
            return None
    @property
    def access_db_objects(self,):
        selector = getattr(self.model_dependency, f'select_{self.model_slug}', None)
        if selector:
            return selector.model_class.objects
        return None
    @property
    def access_db(self,):
        selector = getattr(self.model_dependency, f'select_{self.model_slug}', None)
        if selector:
            return selector.model_class
        return None
