from django_abstract.utilities import ClassInfoProvider,ServiceEntryData,ServiceDataOperator
from django.core.exceptions import ValidationError
from django_abstract.log.utilities import ErrorSuccessLogger
from django.utils import timezone

class BaseOperatorService(ClassInfoProvider):
    model_dependency=None
    last_updated = None
    hooks_list = []
    operator_class = ServiceDataOperator
    entry_class = ServiceEntryData
    
    def __init__(self, session_key,*args,include_session=False,**db_required_fields):
        db_required_fields.update( ({'session_key':session_key,} if include_session else {}))
        self.session_key = session_key
        self.db_record = self.read_entry(**db_required_fields)
        self.entry = self.entry_class.load_obj_data(self.db_record)    
        self.operator = self.operator_class(self.entry)
        self.operator.init_default_state()
        super().__init__()
        
    class BaseServiceValidator:
        _MINIMUM_WRITE_FIELDS = []
        _MINIMUM_READ_FIELDS = []
        _SERVICE_DOMAIN_FIELDS = []
        _METHOD_COLLECTION = {}
        
        def __init__(self, **data):
            self.data = data
           #Model fields to avoid random writing!
            self.VALID_FIELDS = {}

        def can_run(self, *required_fields: list[str],dry_run=False, **data) -> bool:
            """Validate required fields are present and not None in data."""
            fields= required_fields if required_fields else ( self._MINIMUM_WRITE_FIELDS or self._MINIMUM_READ_FIELDS)
            raw_data = data if data else self.data
            for field in fields:
                if field not in raw_data or raw_data[field] is None:
                    if not dry_run:
                        raise ValidationError(f"Missing or invalid field: {field}")
                    else:
                        return False
            return True

        def run_service_check(self,*required_fields, **data):
            raw_data = (data or self.data)
            
            check = self.can_run(*required_fields,**raw_data,)
                        
            if check:
                for field in self._SERVICE_DOMAIN_FIELDS:
                    if field in raw_data:
                        self.VALID_FIELDS[field]=raw_data[field]
                return self.VALID_FIELDS

        def regester_method(self,name,method):
            self._METHOD_COLLECTION[name]=method
            return self
        
        def run(self, method_name, data: dict):
            if not self._METHOD_COLLECTION:
                return True
            method =  self._METHOD_COLLECTION.get(method_name,None)
            if method:
                method(data=data)
                return True
            return False
    validator = BaseServiceValidator
    def hook(self, entry):
        
        if self.can_run(**entry.service_data):
            return self.run(**entry.service_data)
        return None
    
    def hook_pad(self,):
        for hook in self.hooks_list:
            hook.hook(obj=self.entry, )
        return True

    def run_skeleten(self, **kwargs):
        """
        Core update method with bulk operation support
        Returns tuple: (updated_object, success_bool)
        """
        if self.is_exists(**kwargs):
            if not self.operator.should_update():
                return self.entry

            self.pending_updates.update(kwargs)
            self.last_updated = timezone.now()

            # Only save every 5 seconds or when explicitly flushed
            if (self.last_updated - getattr(self, '_last_save', timezone.now())).seconds >= 5:
                self.operator.flush_updates(pending_updates=self.pending_updates)
                self.db_record.bulk_update(self.entry.service_data)
                self.db_record.save()
            self.entry.load_obj_data(self.db_record)
            return self.entry
        self.entry.errors['record_exists']=False
        return self.entry
    
    
    
    def read_entry(self, **kwargs):
        data = self.validator(**kwargs).run_service_check()        
        try:
            if self.is_exists(**data):
                
                return self.access_db.get(**data)
            else:
                
                return self.create_entry(**data)
            
        except Exception as e:
            self.logging_hook(operation=f'RETRIEVING {self.session_key.upper()}' , e=e, **kwargs)
            print('WTF',self.model_dependency,e,kwargs,data)
            raise e
        
    def logging_hook(self, operation, e=None, **kwargs):
        """Logs the operation and error message"""
        error_message = f' Failed {operation.lower()} of user {self.session_key} with data {kwargs}. trace back: {e} '
        operation += f' OF USER {self.session_key}'
        return ErrorSuccessLogger().logging_check(operation=operation, service_data=self.get_class_info(), error_message=error_message)

    def is_exists(self,  **kwargs):
        data = self.validator(**kwargs).run_service_check()
        return self.access_db.filter(**data).exists()

    def can_run(self,model_name, **kwargs) -> bool:
        
        validator =  self.validator(entry=self.entry)
        flag = validator.run(method_name=model_name, data=kwargs)
        """if flag:
            self.entry.service_data = validator.behavior.service_data"""
        return flag

    def delete_entry(self,):
        return self.access_db.delete(id=self.entry.obj_id)

    def create_entry(self,**kwargs):
        data = self.validator(**kwargs).run_service_check()
        return self.access_db.create(**data)

    @property
    def access_db(self,):
        return self.model_dependency().model_class.objects