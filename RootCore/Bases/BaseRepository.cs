using Microsoft.EntityFrameworkCore;
using RootCore.Database;
using RootCore.Response;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace RootCore.Bases
{
    /// <summary>
    /// Base repository with common CRUD operations.
    /// </summary>
    /// <typeparam name="T">Entity type that inherits from BaseModel</typeparam>
    public class BaseRepository<T> where T : BaseModel
    {
        protected readonly DbContext _context;
        protected readonly DbSet<T> _dbSet;

        public BaseRepository(DbContext context)
        {
            _context = context;
            _dbSet = context.Set<T>();
        }

        /// <summary>
        /// Get all items without pagination.
        /// </summary>
        public virtual async Task<List<T>> GetAllAsync(bool includeDeleted = false)
        {
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();
            
            return await query.ToListAsync();
        }

        /// <summary>
        /// Get a single item by ID.
        /// </summary>
        public virtual async Task<T?> GetByIdAsync(int id, bool includeDeleted = false)
        {
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();
            
            return await query.FirstOrDefaultAsync(e => e.Id == id);
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
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();

            if (filter != null)
            {
                query = query.Where(filter);
            }

            var total = await query.CountAsync();
            var items = await query
                .Skip((page - 1) * perPage)
                .Take(perPage)
                .ToListAsync();

            return new PaginatedResponse<T>(items, total, page, perPage);
        }

        /// <summary>
        /// Get multiple items without pagination metadata.
        /// </summary>
        public virtual async Task<List<T>> GetManyAsync(
            int skip = 0, 
            int limit = 100, 
            bool includeDeleted = false,
            Expression<Func<T, bool>>? filter = null)
        {
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();

            if (filter != null)
            {
                query = query.Where(filter);
            }

            return await query.Skip(skip).Take(limit).ToListAsync();
        }

        /// <summary>
        /// Create a new item.
        /// </summary>
        public virtual async Task<T> CreateAsync(T entity)
        {
            await _dbSet.AddAsync(entity);
            await _context.SaveChangesAsync();
            return entity;
        }

        /// <summary>
        /// Update an existing item.
        /// </summary>
        public virtual async Task<T> UpdateAsync(T entity)
        {
            _dbSet.Update(entity);
            await _context.SaveChangesAsync();
            return entity;
        }

        /// <summary>
        /// Soft delete an item.
        /// </summary>
        public virtual async Task<bool> SoftDeleteAsync(int id)
        {
            var entity = await GetByIdAsync(id);
            if (entity == null)
                return false;

            entity.IsDeleted = true;
            await _context.SaveChangesAsync();
            return true;
        }

        /// <summary>
        /// Restore a soft deleted item.
        /// </summary>
        public virtual async Task<bool> RestoreAsync(int id)
        {
            var entity = await GetByIdAsync(id, includeDeleted: true);
            if (entity == null || !entity.IsDeleted)
                return false;

            entity.IsDeleted = false;
            await _context.SaveChangesAsync();
            return true;
        }

        /// <summary>
        /// Permanently delete an item.
        /// </summary>
        public virtual async Task<bool> ForceDeleteAsync(int id)
        {
            var entity = await GetByIdAsync(id, includeDeleted: true);
            if (entity == null)
                return false;

            _dbSet.Remove(entity);
            await _context.SaveChangesAsync();
            return true;
        }

        /// <summary>
        /// Check if an item exists.
        /// </summary>
        public virtual async Task<bool> ExistsAsync(int id, bool includeDeleted = false)
        {
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();
            
            return await query.AnyAsync(e => e.Id == id);
        }

        /// <summary>
        /// Count items matching filters.
        /// </summary>
        public virtual async Task<int> CountAsync(
            bool includeDeleted = false,
            Expression<Func<T, bool>>? filter = null)
        {
            var query = includeDeleted 
                ? _dbSet.IgnoreQueryFilters() 
                : _dbSet.AsQueryable();

            if (filter != null)
            {
                query = query.Where(filter);
            }

            return await query.CountAsync();
        }

        /// <summary>
        /// Bulk create multiple items.
        /// </summary>
        public virtual async Task<List<T>> BulkCreateAsync(List<T> entities)
        {
            await _dbSet.AddRangeAsync(entities);
            await _context.SaveChangesAsync();
            return entities;
        }

        /// <summary>
        /// Bulk update multiple items.
        /// </summary>
        public virtual async Task<List<T>> BulkUpdateAsync(List<T> entities)
        {
            _dbSet.UpdateRange(entities);
            await _context.SaveChangesAsync();
            return entities;
        }

        /// <summary>
        /// Bulk delete multiple items.
        /// </summary>
        public virtual async Task<int> BulkDeleteAsync(List<int> ids)
        {
            var entities = await _dbSet.Where(e => ids.Contains(e.Id)).ToListAsync();
            foreach (var entity in entities)
            {
                entity.IsDeleted = true;
            }
            await _context.SaveChangesAsync();
            return entities.Count;
        }
    }
}
