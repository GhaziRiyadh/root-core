using System;

namespace RootCore.Exceptions
{
    public class RootCoreException : Exception
    {
        public RootCoreException(string message) : base(message)
        {
        }

        public RootCoreException(string message, Exception innerException) 
            : base(message, innerException)
        {
        }
    }

    public class NotFoundException : RootCoreException
    {
        public NotFoundException(string message) : base(message)
        {
        }
    }

    public class ValidationException : RootCoreException
    {
        public ValidationException(string message) : base(message)
        {
        }
    }

    public class ServiceException : RootCoreException
    {
        public ServiceException(string message) : base(message)
        {
        }

        public ServiceException(string message, Exception innerException) 
            : base(message, innerException)
        {
        }
    }

    public class OperationException : RootCoreException
    {
        public OperationException(string message) : base(message)
        {
        }
    }
}
