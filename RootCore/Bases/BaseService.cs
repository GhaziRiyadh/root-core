using RootCore.Database;
using RootCore.Exceptions;
using RootCore.Response;
using System;
using System.Collections.Generic;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace RootCore.Bases
{
    /// <summary>
    /// Base service class with common CRUD operations and standardized responses.
    /// </summary>
    /// <typeparam name="T">Entity type that inherits from BaseModel</typeparam>
    public class BaseService<T> where T : BaseModel
    {
        protected readonly BaseRepository<T> _repository;

        public BaseService(BaseRepository<T> repository)
        {
            _repository = repository;
        }

        /// <summary>
        /// Transform data before returning (override in subclasses).
        /// </summary>
        protected virtual Task<T> TransformOneDataAsync(T data)
        {
            return Task.FromResult(data);
        }

        /// <summary>
        /// Transform multiple data items before returning.
        /// </summary>
        protected virtual async Task<List<T>> TransformMultiDataAsync(List<T> data)
        {
            var result = new List<T>();
            foreach (var item in data)
            {
                result.Add(await TransformOneDataAsync(item));
            }
            return result;
        }

        /// <summary>
        /// Get all items without pagination.
        /// </summary>
        public virtual async Task<ApiResponse<List<T>>> GetAllAsync(bool includeDeleted = false)
        {
            try
            {
                var items = await _repository.GetAllAsync(includeDeleted);
                var transformedItems = await TransformMultiDataAsync(items);
                return new ApiResponse<List<T>>(
                    transformedItems, 
                    $"Retrieved {items.Count} items successfully"
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error retrieving all items: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Get a single item by ID.
        /// </summary>
        public virtual async Task<ApiResponse<T>> GetByIdAsync(int id, bool includeDeleted = false)
        {
            try
            {
                var item = await _repository.GetByIdAsync(id, includeDeleted);
                
                if (item == null)
                {
                    throw new NotFoundException($"Item with id {id} not found");
                }

                var transformedItem = await TransformOneDataAsync(item);
                return new ApiResponse<T>(transformedItem, "Item retrieved successfully");
            }
            catch (NotFoundException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error retrieving item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Get paginated list of items.
        /// </summary>
        public virtual async Task<PaginatedResponse<T>> GetListAsync(
            int page = 1,
            int perPage = 10,
            bool includeDeleted = false,
            Expression<Func<T, bool>>? filter = null)
        {
            try
            {
                // Validate pagination parameters
                if (page < 1) page = 1;
                if (perPage < 1 || perPage > 100) perPage = 10;

                var result = await _repository.GetListAsync(page, perPage, includeDeleted, filter);
                var transformedItems = await TransformMultiDataAsync(result.Items);
                
                return new PaginatedResponse<T>(
                    transformedItems,
                    result.Total,
                    result.Page,
                    result.PerPage,
                    result.Message
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error retrieving items list: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Get multiple items without pagination metadata.
        /// </summary>
        public virtual async Task<ApiResponse<List<T>>> GetManyAsync(
            int skip = 0,
            int limit = 100,
            bool includeDeleted = false,
            Expression<Func<T, bool>>? filter = null)
        {
            try
            {
                var items = await _repository.GetManyAsync(skip, limit, includeDeleted, filter);
                var transformedItems = await TransformMultiDataAsync(items);
                
                return new ApiResponse<List<T>>(
                    transformedItems,
                    $"Retrieved {items.Count} items successfully"
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error retrieving items: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Create a new item.
        /// </summary>
        public virtual async Task<ApiResponse<T>> CreateAsync(T entity)
        {
            try
            {
                // Validate business rules before creation
                await ValidateCreateAsync(entity);
                
                var item = await _repository.CreateAsync(entity);
                var transformedItem = await TransformOneDataAsync(item);
                
                return new ApiResponse<T>(transformedItem, "Item created successfully");
            }
            catch (ValidationException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error creating item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Update an existing item.
        /// </summary>
        public virtual async Task<ApiResponse<T>> UpdateAsync(int id, T entity)
        {
            try
            {
                // Check if item exists
                var existingItem = await _repository.GetByIdAsync(id);
                if (existingItem == null)
                {
                    throw new NotFoundException($"Item with id {id} not found");
                }

                // Validate business rules before update
                await ValidateUpdateAsync(id, entity, existingItem);

                entity.Id = id;
                var updatedItem = await _repository.UpdateAsync(entity);
                var transformedItem = await TransformOneDataAsync(updatedItem);
                
                return new ApiResponse<T>(transformedItem, "Item updated successfully");
            }
            catch (NotFoundException)
            {
                throw;
            }
            catch (ValidationException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error updating item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Soft delete an item.
        /// </summary>
        public virtual async Task<ApiResponse<object>> SoftDeleteAsync(int id)
        {
            try
            {
                // Check if item exists
                var existingItem = await _repository.GetByIdAsync(id);
                if (existingItem == null)
                {
                    throw new NotFoundException($"Item with id {id} not found");
                }

                // Validate if soft delete is allowed
                await ValidateDeleteAsync(id, existingItem);

                var success = await _repository.SoftDeleteAsync(id);
                
                if (!success)
                {
                    throw new OperationException($"Failed to soft delete item with id {id}");
                }

                return new ApiResponse<object>(null!, "Item soft deleted successfully");
            }
            catch (NotFoundException)
            {
                throw;
            }
            catch (ValidationException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error soft deleting item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Restore a soft deleted item.
        /// </summary>
        public virtual async Task<ApiResponse<object>> RestoreAsync(int id)
        {
            try
            {
                var success = await _repository.RestoreAsync(id);
                
                if (!success)
                {
                    throw new NotFoundException($"Item with id {id} not found or not deleted");
                }

                return new ApiResponse<object>(null!, "Item restored successfully");
            }
            catch (NotFoundException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error restoring item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Permanently delete an item.
        /// </summary>
        public virtual async Task<ApiResponse<object>> ForceDeleteAsync(int id)
        {
            try
            {
                // Check if item exists
                var existingItem = await _repository.GetByIdAsync(id, includeDeleted: true);
                if (existingItem == null)
                {
                    throw new NotFoundException($"Item with id {id} not found");
                }

                // Validate if force delete is allowed
                await ValidateForceDeleteAsync(id, existingItem);

                var success = await _repository.ForceDeleteAsync(id);
                
                if (!success)
                {
                    throw new OperationException($"Failed to delete item with id {id}");
                }

                return new ApiResponse<object>(null!, "Item permanently deleted successfully");
            }
            catch (NotFoundException)
            {
                throw;
            }
            catch (ValidationException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error deleting item: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Check if an item exists.
        /// </summary>
        public virtual async Task<ApiResponse<Dictionary<string, bool>>> ExistsAsync(
            int id, 
            bool includeDeleted = false)
        {
            try
            {
                var exists = await _repository.ExistsAsync(id, includeDeleted);
                
                return new ApiResponse<Dictionary<string, bool>>(
                    new Dictionary<string, bool> { { "exists", exists } },
                    $"Item {(exists ? "exists" : "does not exist")}"
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error checking item existence: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Count items matching filters.
        /// </summary>
        public virtual async Task<ApiResponse<Dictionary<string, int>>> CountAsync(
            bool includeDeleted = false,
            Expression<Func<T, bool>>? filter = null)
        {
            try
            {
                var count = await _repository.CountAsync(includeDeleted, filter);
                
                return new ApiResponse<Dictionary<string, int>>(
                    new Dictionary<string, int> { { "count", count } },
                    $"Found {count} items"
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error counting items: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Create multiple items in bulk.
        /// </summary>
        public virtual async Task<ApiResponse<List<T>>> BulkCreateAsync(List<T> entities)
        {
            try
            {
                foreach (var entity in entities)
                {
                    await ValidateCreateAsync(entity);
                }

                var items = await _repository.BulkCreateAsync(entities);
                var transformedItems = await TransformMultiDataAsync(items);
                
                return new ApiResponse<List<T>>(
                    transformedItems,
                    $"Successfully created {items.Count} items"
                );
            }
            catch (ValidationException)
            {
                throw;
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error in bulk creating items: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Bulk delete multiple items.
        /// </summary>
        public virtual async Task<ApiResponse<int>> BulkDeleteAsync(List<int> ids)
        {
            try
            {
                var count = await _repository.BulkDeleteAsync(ids);
                
                return new ApiResponse<int>(
                    count,
                    $"Successfully deleted {count} items"
                );
            }
            catch (Exception ex)
            {
                throw new ServiceException($"Error bulk deleting items: {ex.Message}", ex);
            }
        }

        // Validation methods to be overridden by subclasses
        protected virtual Task ValidateCreateAsync(T entity)
        {
            return Task.CompletedTask;
        }

        protected virtual Task ValidateUpdateAsync(int id, T entity, T existingItem)
        {
            return Task.CompletedTask;
        }

        protected virtual Task ValidateDeleteAsync(int id, T existingItem)
        {
            return Task.CompletedTask;
        }

        protected virtual Task ValidateForceDeleteAsync(int id, T existingItem)
        {
            return Task.CompletedTask;
        }
    }
}
