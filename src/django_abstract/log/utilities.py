from django_abstract.log.services.creators_dependency import get_creator_manager

LDM = get_creator_manager()

class SystemErrorLoggerUtility:
    """
    Utility class for handling system error logging.
    Encapsulates operations related to the SystemErrorLog model.
    """
    
    def __init__(self,
        error_message=None,
        service_name=None,
        app_name=None,
        method_name=None,
        action=None,
        notes=None,
        reported_by=None,
        is_active=True,
        resolved = False,
        ):
        self.error_message = error_message
        self.service_name = service_name
        self.app_name = app_name
        self.method_name = method_name
        self.action = action
        self.reported_by = service_name or self.__class__.__name__
        self.notes = notes
        self.resolved = resolved
        self.is_active = is_active # models.BooleanField()
        self.reported_by = reported_by,

    @classmethod
    def log_error(cls):
        
        return cls(
            error_message =None,
            service_name =None,
            app_name =None,
            method_name =None,
            action =None,
            reported_by =None,
            notes =None,
        )

    def to_dict(self,):
        """
        Retrieves system error logs based on filters.
        """
        return {
        'error_message' : self.error_message,
        'service_name' : self.service_name,
        'app_name' : self.app_name,
        'method_name' : self.method_name,
        'action' : self.action,
        'reported_by' : self.reported_by,
        'notes' : self.notes,
        'resolved' : self.resolved,
        'is_active':self.is_active,
        }

    def log_it(self) -> dict[str,str]:
        data = self.to_dict()
        LDM.create_system_error_log.model_class.objects.create(**data)
        return data

class SystemSuccessLoggerUtility:

    def __init__(self,
             success_message=None,
             service_name=None,
             app_name=None,
             method_name=None,
             action=None,
             success_code=None,
             created_by=None,
             ):
            self.success_message = success_message
            self.service_name = service_name
            self.app_name = app_name
            self.method_name = method_name
            self.action = action
            self.success_code = success_code
            self.reported_by = service_name or self.__class__.__name__
            self.created_by = created_by
            self.system_success_log = []
    def to_dict(self,):
        """
        Retrieves system error logs based on filters.
        """
        return {
        'success_message' : self.success_message,
        'service_name' : self.service_name,
        'app_name' : self.app_name,
        'method_name' : self.method_name,
        'action' : self.action,
        'reported_by' : self.reported_by,
        "created_by":self.created_by,

        }
    def logg_it(self,):
        instance = self.success_logger(
            success_message=self.success_message,
            service_name=self.service_name,
            app_name=self.app_name,
            method_name=self.method_name,
            action=self.action,
            success_code=self.success_code,
            created_by=self.created_by,
        )
        self.system_success_log.append(instance)
        return self.to_dict()
    @classmethod
    def success_logger(cls,
                       success_message=None,
                       service_name=None,
                       app_name=None,
                       method_name=None,
                       action=None,
                       success_code=None,
                       created_by=None,
                       ):
        return cls(
            success_message=success_message,
            service_name=service_name,
            app_name=app_name,
            method_name=method_name,
            action=action,
            success_code=success_code,
            created_by=created_by,
        )

class ErrorSuccessLogger:
    def __init__(self):
         self._success_logger = SystemSuccessLoggerUtility()
         self._error_logger = SystemErrorLoggerUtility()

    def logging_check(self,operation, error_message=None,success_message=None, service_data=None,) -> dict[str,str]:
        if not error_message:
            logger = self._success_logger.success_logger()
            logger.success_message = success_message or 'no sucess message!!'
            logger.service_name = service_data['service_name'],
            logger.app_name = service_data['app_name'],
            logger.method_name = service_data['method_name'],
            logger.action = operation,
        else:
            logger_instance_message = f"Failed to {operation.lower()} : {str(error_message)}"
            logger = self._error_logger.log_error()
            logger.service_name=service_data['service_name'],
            logger.app_name=service_data['app_name'],
            logger.error_message=logger_instance_message,
            logger.method_name= service_data['method_name'],
            logger.action=operation,
        return logger.log_it()

def log_event(event_type, action, user=None, metadata=None):
    return LDM.create_log_event.model_class.objects.create(
        user=user,
        event_type=event_type,
        action=action,
        metadata=metadata or {}
    )
