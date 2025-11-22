using System.Collections.Generic;

namespace RootCore.Response
{
    /// <summary>
    /// Standard API response wrapper.
    /// </summary>
    /// <typeparam name="T">Type of data</typeparam>
    public class ApiResponse<T>
    {
        public T Data { get; set; }
        public string Message { get; set; }
        public bool Success { get; set; } = true;

        public ApiResponse(T data, string message = "Success")
        {
            Data = data;
            Message = message;
        }
    }

    /// <summary>
    /// Paginated response for list endpoints.
    /// </summary>
    /// <typeparam name="T">Type of items</typeparam>
    public class PaginatedResponse<T>
    {
        public List<T> Items { get; set; }
        public int Total { get; set; }
        public int Page { get; set; }
        public int PerPage { get; set; }
        public int Pages { get; set; }
        public string Message { get; set; }

        public PaginatedResponse(List<T> items, int total, int page, int perPage, string message = "Success")
        {
            Items = items;
            Total = total;
            Page = page;
            PerPage = perPage;
            Pages = (int)Math.Ceiling((double)total / perPage);
            Message = message;
        }
    }

    /// <summary>
    /// Error response for API errors.
    /// </summary>
    public class ErrorResponse
    {
        public string Message { get; set; }
        public string? Detail { get; set; }
        public bool Success { get; set; } = false;

        public ErrorResponse(string message, string? detail = null)
        {
            Message = message;
            Detail = detail;
        }
    }
}
