using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using RootCore.Database;
using RootCore.Exceptions;
using RootCore.Response;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace RootCore.Bases
{
    /// <summary>
    /// Base controller with common CRUD endpoints.
    /// </summary>
    /// <typeparam name="T">Entity type that inherits from BaseModel</typeparam>
    [ApiController]
    [Route("api/[controller]")]
    public abstract class BaseController<T> : ControllerBase where T : BaseModel
    {
        protected readonly BaseService<T> _service;

        public BaseController(BaseService<T> service)
        {
            _service = service;
        }

        /// <summary>
        /// Get all items without pagination.
        /// </summary>
        [HttpGet("all")]
        public virtual async Task<ActionResult<ApiResponse<List<T>>>> GetAll([FromQuery] bool includeDeleted = false)
        {
            try
            {
                var result = await _service.GetAllAsync(includeDeleted);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Get paginated list of items.
        /// </summary>
        [HttpGet]
        public virtual async Task<ActionResult<PaginatedResponse<T>>> GetList(
            [FromQuery] int page = 1,
            [FromQuery] int perPage = 10,
            [FromQuery] bool includeDeleted = false)
        {
            try
            {
                var result = await _service.GetListAsync(page, perPage, includeDeleted);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Get a single item by ID.
        /// </summary>
        [HttpGet("{id}")]
        public virtual async Task<ActionResult<ApiResponse<T>>> GetById(int id, [FromQuery] bool includeDeleted = false)
        {
            try
            {
                var result = await _service.GetByIdAsync(id, includeDeleted);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Create a new item.
        /// </summary>
        [HttpPost]
        public virtual async Task<ActionResult<ApiResponse<T>>> Create([FromBody] T entity)
        {
            try
            {
                var result = await _service.CreateAsync(entity);
                return CreatedAtAction(nameof(GetById), new { id = result.Data.Id }, result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Update an existing item.
        /// </summary>
        [HttpPut("{id}")]
        public virtual async Task<ActionResult<ApiResponse<T>>> Update(int id, [FromBody] T entity)
        {
            try
            {
                var result = await _service.UpdateAsync(id, entity);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Soft delete an item.
        /// </summary>
        [HttpDelete("{id}")]
        public virtual async Task<ActionResult<ApiResponse<object>>> Delete(int id)
        {
            try
            {
                var result = await _service.SoftDeleteAsync(id);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Restore a soft deleted item.
        /// </summary>
        [HttpPost("{id}/restore")]
        public virtual async Task<ActionResult<ApiResponse<object>>> Restore(int id)
        {
            try
            {
                var result = await _service.RestoreAsync(id);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Permanently delete an item.
        /// </summary>
        [HttpDelete("{id}/force")]
        public virtual async Task<ActionResult<ApiResponse<object>>> ForceDelete(int id)
        {
            try
            {
                var result = await _service.ForceDeleteAsync(id);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Check if an item exists.
        /// </summary>
        [HttpGet("{id}/exists")]
        public virtual async Task<ActionResult<ApiResponse<Dictionary<string, bool>>>> Exists(
            int id, 
            [FromQuery] bool includeDeleted = false)
        {
            try
            {
                var result = await _service.ExistsAsync(id, includeDeleted);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Count items.
        /// </summary>
        [HttpGet("count")]
        public virtual async Task<ActionResult<ApiResponse<Dictionary<string, int>>>> Count(
            [FromQuery] bool includeDeleted = false)
        {
            try
            {
                var result = await _service.CountAsync(includeDeleted);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Bulk create items.
        /// </summary>
        [HttpPost("bulk")]
        public virtual async Task<ActionResult<ApiResponse<List<T>>>> BulkCreate([FromBody] List<T> entities)
        {
            try
            {
                var result = await _service.BulkCreateAsync(entities);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Bulk delete items.
        /// </summary>
        [HttpPost("bulk-delete")]
        public virtual async Task<ActionResult<ApiResponse<int>>> BulkDelete([FromBody] List<int> ids)
        {
            try
            {
                var result = await _service.BulkDeleteAsync(ids);
                return Ok(result);
            }
            catch (Exception ex)
            {
                return HandleException(ex);
            }
        }

        /// <summary>
        /// Handle exceptions and return appropriate HTTP responses.
        /// </summary>
        protected ActionResult HandleException(Exception ex)
        {
            return ex switch
            {
                NotFoundException notFoundEx => NotFound(new ErrorResponse(notFoundEx.Message)),
                ValidationException validationEx => BadRequest(new ErrorResponse(validationEx.Message)),
                OperationException opEx => BadRequest(new ErrorResponse(opEx.Message)),
                ServiceException serviceEx => StatusCode(500, new ErrorResponse(serviceEx.Message, serviceEx.InnerException?.Message)),
                _ => StatusCode(500, new ErrorResponse("An unexpected error occurred", ex.Message))
            };
        }
    }
}
