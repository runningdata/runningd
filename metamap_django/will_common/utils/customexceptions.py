class RDException(Exception):
    def __init__(self, message, err_stack):
        super(RDException, self).__init__(message, err_stack)
        self.message = message
        self.err_stack = err_stack
