from django_abstract.utilities import ClassInfoProvider,ServiceEntryData,ServiceDataOperator
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django_abstract.log.utilities import ErrorSuccessLogger
from django.utils import timezone
from functools import partial

class BaseOperatorService(ClassInfoProvider):
    """Core service base class combining model dependencies, validation, and database operations.

    Attributes:
        model_dependency: The dependency injection container for models.
        model_slug (str): Slug identifier for the model.
        last_updated (datetime): Timestamp of the last bulk update.
        hooks_list (list): List of allowed hooks.
        operator_class (Type): Class used to instantiate the operator.
        entry_class (Type): Class used to instantiate entry data.
    """
    model_dependency= None
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
        load_record=True,
        **db_required_fields,
    ):
        """Initialize the BaseOperatorService.

        Args:
            session_key (str): The session identifier.
            *args: Variable length argument list.
            include_session (bool, optional): Whether to inject the session key into DB operations. Defaults to False.
            include_session_key_as (str, optional): Custom field name for the session key.
            auto_create (bool, optional): Whether to automatically create a record if not found. Defaults to False.
            load_record (bool, optional): Whether to immediately load the record from the DB. Defaults to True.
            **db_required_fields: Initial required fields for database lookup.
        """
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
        self.load_record = load_record
        self.__db_required_fields = db_required_fields
        super().__init__()
        self.validator = self.BaseServiceValidator

        self.model_dependency=self.model_dependency
        self.model_slug=self.model_slug
        self.last_updated=self.last_updated
        self.hooks_list=self.hooks_list
        self.operator_class=self.operator_class
        self.entry_class=self.entry_class
    def init_state_hook(self):
        if self.load_record:
            self.db_record = self.read_entry(**self.__db_required_fields)

            self.entry = self.entry_class.load_obj_data(self.db_record)
        else:
            self.entry = self.entry_class()

        self.operator = self.operator_class(self.entry)
        self.operator.init_default_state()

    class BaseServiceValidator:
        def __init__(self,dependency,parent_service=None, skip_check=False,**data):
            self.MINIMUM_WRITE_FIELDS = []
            self.MINIMUM_READ_FIELDS = []
            self.SERVICE_DOMAIN_FIELDS = []
            self.METHOD_COLLECTION = {}
            self.RESERVED_DB_METHODS = {
                "read_entry":[],
                "delete_entry":[],
                "create_entry":[],
            }
            self.parent_service = parent_service
            self.skip_check = skip_check
            self.data = data
            self.dependency = dependency
            # Model fields to avoid random writing!
            self.VALID_FIELDS = {}
            self.VALID_FIELDS_PER_ACTION = {} # {method_name:[valid_fields]} to avoid random writing per action!
            self.cross_domain_data = {}
            self.is_cross_domain = False
            self.target_method = None
            self.behavior = ServiceEntryData()
            self.meta_hook()
            self.load_db_methods()
            if not self.skip_check:
                self.run_service_check()

        def load_settings(self,settings):
            self.RESERVED_DB_METHODS = settings.RESERVED_DB_METHODS
            self.MINIMUM_WRITE_FIELDS = settings.MINIMUM_WRITE_FIELDS
            self.SERVICE_DOMAIN_FIELDS = settings.SERVICE_DOMAIN_FIELDS
            self.VALID_FIELDS = settings.VALID_FIELDS
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
            raise NotImplementedError()

        def parent_service_hook(self,parent_instance):
            """Lifecycle hook: Override in subclasses to build registries before validation."""

            self.parent_service=parent_instance

        def set_db_methods_fields(self,method_name, *required_fields):

            if method_name in self.RESERVED_DB_METHODS:
                self.RESERVED_DB_METHODS[method_name]=list(required_fields)            

        def load_db_methods(self,):
            for method_name in self.RESERVED_DB_METHODS:
                method = getattr(self.parent_service, method_name, None)
                if method:
                    self.METHOD_COLLECTION[method_name] = self.parent_service_method_proxy(method_name, method)

        def parent_service_method_proxy(self,method_name,method):

            def proxy(method_name, method):
                self.data["method_name"]=method_name
                data = self.run_service_check()
                return  method(skip_validation=True, **data)

            return partial(proxy, method_name, method)

        def run_service_check(self,*required_fields, **data):
            raw_data = (data or self.data)
            method_name = raw_data.get("method_name")
            self.target_method = method_name
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

        def get_method_args(self, method_name, keys=False):
            valid_fields = (self.RESERVED_DB_METHODS if method_name in self.RESERVED_DB_METHODS else self.VALID_FIELDS_PER_ACTION).get(method_name, [])
            if keys:
                return valid_fields
            valid_domain_fields = self.run_service_check(*valid_fields,)
            if self.is_cross_domain:
                return [valid_domain_fields.get(field) for field in self.cross_domain_data.keys() if field in valid_domain_fields]
            return [valid_domain_fields.get(field) for field in valid_fields]

        def run(self, method_name,):
            is_db_method = method_name in self.RESERVED_DB_METHODS
            if not method_name:
                return False
            if not self.METHOD_COLLECTION and method_name not in self.RESERVED_DB_METHODS:
                return False

            method =  self.METHOD_COLLECTION.get(method_name,None)
            if method:
                if is_db_method:
                    data = method()
                    self.behavior.service_data.update(
                        model_to_dict(data)
                    )

                else:
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
        service_args = entry.service_data.get("service_args")
        if hook_names and not all([(hook_name in self.hooks_list) for hook_name in hook_names]):
            return False
        if hook_names:
            from django_abstract.registry import get_service
            for hook_name in hook_names:
                target_service = get_service(hook_name)

                if target_service and hasattr(target_service, 'hook'):
                    target_service(**service_args).hook(entry=(entry or self.entry))

            # for hook in self.hooks_list:
            #     target_service = SERVICE_REGISTRY['MODEL_SERVICE'].get(hook)
            #     if not target_service:
            #         target_service = SERVICE_REGISTRY['BARE_SERVICE'].get(hook)
            #     if target_service and hasattr(target_service, 'hook'):
            #         target_service.hook(obj=entry or self.entry, )
            # return True

    def run_skeleten(self, **kwargs) -> ServiceEntryData:
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """

        validator = self.validator(
            dependency=self.model_dependency, parent_service=self,skip_check=not self.load_record, **kwargs
        )
        validator.run(
            method_name=validator.data.get('method_name'),
        )
        self.entry.service_data = validator.behavior.service_data
        if self.load_record:
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

    def read_entry(self,skip_validation=False, **kwargs):

        if not skip_validation:
            kwargs["method_name"]="read_entry"
            validator = self.validator(
                self.model_dependency, parent_service=self,skip_check=not self.load_record, **kwargs
            )
            data = validator.run_service_check()   
        else:
            data = kwargs
        try:
            if self.is_exists(skip_validation=True, **data):

                return self.access_db_objects.filter(**data).first()
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

    def is_exists(self, skip_validation=False, **kwargs,):
        if not skip_validation:
            data = self.validator(
                self.model_dependency, parent_service=self,skip_check=not self.load_record, **kwargs
            ).run_service_check()
        else:
            data=kwargs
        return self.access_db_objects.filter(**data).exists()

    def can_run(self,method_name, **kwargs) -> bool:
        validator =  self.validator(self.model_dependency,skip_check= not self.load_record,**kwargs)
        required_fields = validator.get_method_args(method_name,keys=True)
        flag = validator.can_run(*required_fields,)
        return flag

    def delete_entry(selfskip_validation=False, **kwargs):

        if not skip_validation:
            validator = self.validator(
                self.model_dependency,
                parent_service=self,
                skip_check=not self.load_record,
                **kwargs,
            )
            data = validator.run_service_check()
        else:
            data = kwargs
        self.db_record = None
        return self.access_db_objects.delete(**data)

    def create_entry(self,skip_validation=False, **kwargs):
        if not skip_validation:
            validator = self.validator(
                self.model_dependency, parent_service=self,skip_check=not self.load_record, **kwargs
            )
            data = validator.run_service_check()
        else:
            data = kwargs
        if data:

            obj = self.access_db_objects.create(**data)     
            if hasattr(self,'entry'):
                self.entry.raw_data['db_record']=obj
            return obj
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
