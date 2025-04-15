# Templates
TEMPLATE_INTERFACE = """using {namespace}.Domain.Entity;
using {namespace}.Infrastructure.Base;

namespace {namespace}.Infrastructure.Abstractions;

public interface I{name}Repository : IRepository<{name}>
{{
}}
"""

TEMPLATE_IMPLEMENTATION = """using {namespace}.Domain.Entity;
using {namespace}.Infrastructure.Abstractions;
using {namespace}.Infrastructure.Base;
using {namespace}.Infrastructure.Context;

namespace {namespace}.Infrastructure.Repositories;

internal class {name}Repository : Repository<{name}>, I{name}Repository
{{
    public {name}Repository({context_class} context) : base(context)
    {{
    }}
}}
"""

TEMPLATE_UOW_INTERFACE_HEADER = """using {namespace}.Infrastructure.Abstractions;
namespace {namespace}.Infrastructure.Base;

public interface IUnitOfWork : IDisposable, IAsyncDisposable
{{
"""

TEMPLATE_UOW_INTERFACE_FOOTER = """    public bool IsTransactionStarted { get; }
    IRepository<T> GetRepository<T>() where T : class;
    TRepository GetCustomRepository<TRepository>() where TRepository : class;

    Task BeginTransactionAsync(CancellationToken cancellationToken = default);
    Task CommitTransactionAsync(CancellationToken cancellationToken = default);
    Task RollbackTransactionAsync(CancellationToken cancellationToken = default);
    Task<int> SaveChangesAsync(CancellationToken cancellationToken = default);
}
"""

TEMPLATE_UOW_IMPL_HEADER = """using System.Collections.Concurrent;
using Microsoft.EntityFrameworkCore.Storage;
using Microsoft.Extensions.DependencyInjection;
using {namespace}.Domain.Exceptions;
using {namespace}.Infrastructure.Context;
using {namespace}.Infrastructure.Abstractions;
namespace {namespace}.Infrastructure.Base;

public class UnitOfWork : IUnitOfWork
{{
    private readonly {context_class} _context;
    private readonly ConcurrentDictionary<Type, object> _customRepositories = new();
    private readonly ConcurrentDictionary<Type, object> _repositories = new();
    private readonly IServiceProvider _serviceProvider;
    private bool _disposed;
    private IDbContextTransaction? _transaction;

    public UnitOfWork({context_class} context, IServiceProvider serviceProvider)
    {{
        _context = context ?? throw new ArgumentNullException(nameof(context));
        _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
    }}

    public bool IsTransactionStarted => _transaction is not null;

"""

TEMPLATE_UOW_IMPL_REPO_PROPERTY = """    public {interface_name} {property_name} => GetCustomRepository<{interface_name}>();\n"""

TEMPLATE_UOW_IMPL_FOOTER = """
    public IRepository<T> GetRepository<T>() where T : class =>
        (IRepository<T>)_repositories.GetOrAdd(typeof(T), _ => _serviceProvider.GetRequiredService<IRepository<T>>());

    public TRepository GetCustomRepository<TRepository>() where TRepository : class =>
        (TRepository)_customRepositories.GetOrAdd(typeof(TRepository), _ => _serviceProvider.GetRequiredService<TRepository>());

    public async Task BeginTransactionAsync(CancellationToken cancellationToken = default) =>
        _transaction ??= await _context.Database.BeginTransactionAsync(cancellationToken);

    public async Task CommitTransactionAsync(CancellationToken cancellationToken = default)
    {{
        if (_transaction is null) throw new TransactionException();
        await _transaction.CommitAsync(cancellationToken);
        await _transaction.DisposeAsync();
        _transaction = null;
    }}

    public async Task RollbackTransactionAsync(CancellationToken cancellationToken = default)
    {{
        if (_transaction is null) return;
        await _transaction.RollbackAsync(cancellationToken);
        await _transaction.DisposeAsync();
        _transaction = null;
    }}

    public async Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {{
        if (_transaction is not null) throw new TransactionException();
        return await _context.SaveChangesAsync(cancellationToken);
    }}

    public void Dispose()
    {{
        Dispose(true);
        GC.SuppressFinalize(this);
    }}

    public async ValueTask DisposeAsync()
    {{
        if (!_disposed)
        {{
            if (_transaction is not null)
            {{
                await _transaction.DisposeAsync();
                _transaction = null;
            }}

            await _context.DisposeAsync();
            _disposed = true;
        }}

        GC.SuppressFinalize(this);
    }}

    protected virtual void Dispose(bool disposing)
    {{
        if (_disposed) return;

        if (disposing)
        {{
            _transaction?.Dispose();
            _context.Dispose();
        }}

        _disposed = true;
    }}
}
"""

TEMPLATE_REPOSITORY_INTERFACE_WITH_COMMENTS = """using System.Linq.Expressions;

namespace {namespace}.Infrastructure.Base
{{
    /// <summary>
    ///     Generic repository interface for managing entities.
    /// </summary>
    /// <typeparam name="T">The type of entity being managed.</typeparam>
    public interface IRepository<T> where T : class
    {{
        Task<List<T>> GetAllAsync(bool tracking = false, CancellationToken cancellationToken = default);
        Task<List<T>> GetAsync(Expression<Func<T, bool>> predicate, bool tracking = false, CancellationToken cancellationToken = default);
        Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate, Expression<Func<T, TResult>> selector, int skip, int take, bool tracking = false, CancellationToken cancellationToken = default);
        Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate, Expression<Func<T, TResult>> selector, bool tracking = false, CancellationToken cancellationToken = default);
        Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate, Expression<Func<T, TResult>> selector, int skip, int take, string? orderBy = null, bool descending = false, CancellationToken cancellationToken = default);
        Task<T?> GetSingleAsync(Expression<Func<T, bool>> predicate, bool tracking = false, CancellationToken cancellationToken = default);
        Task<TResult?> GetSingleAsync<TResult>(Expression<Func<T, bool>> predicate, Expression<Func<T, TResult>> selector, bool tracking = false, CancellationToken cancellationToken = default);
        Task<T?> FindByIdAsync(int id, CancellationToken cancellationToken = default);
        Task<T?> FindAsync(object[] keyValues, CancellationToken cancellationToken = default);
        Task<T> AddAsync(T entity, CancellationToken cancellationToken = default);
        Task AddRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default);
        Task UpdateAsync(T entity, CancellationToken cancellationToken = default);
        Task UpdateRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default);
        Task RemoveAsync(T entity, CancellationToken cancellationToken = default);
        Task RemoveRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default);
        Task<int> CountAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default);
        Task<bool> AnyAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default);
        Task<bool> AllAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default);
    }}
}}
"""

TEMPLATE_REPOSITORY_IMPLEMENTATION = """using System.Linq.Expressions;
using {namespace}.Infrastructure.Base;
using Microsoft.EntityFrameworkCore;

namespace {namespace}.Infrastructure.Base
{{
    internal class Repository<T> : IRepository<T> where T : class
    {{
        private readonly DbSet<T> _dbSet;

        protected Repository(DbContext dbContext)
        {{
            var context = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
            _dbSet = context.Set<T>();
        }}

        public async Task<List<T>> GetAllAsync(bool tracking = false, CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).ToListAsync(cancellationToken);
        }}

        public async Task<List<T>> GetAsync(Expression<Func<T, bool>> predicate, bool tracking = false,
            CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).Where(predicate).ToListAsync(cancellationToken);
        }}

        public async Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate,
            Expression<Func<T, TResult>> selector, bool tracking = false, CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).Where(predicate).Select(selector)
                .ToListAsync(cancellationToken);
        }}

        public async Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate,
            Expression<Func<T, TResult>> selector, int skip, int take, bool tracking = false,
            CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).Where(predicate).Select(selector)
                .Skip(skip).Take(take).ToListAsync(cancellationToken);
        }}

        public async Task<List<TResult>> GetAsync<TResult>(Expression<Func<T, bool>> predicate,
            Expression<Func<T, TResult>> selector, int skip, int take, string? orderBy = null, bool descending = false,
            CancellationToken cancellationToken = default)
        {{
            // Implementation for the overload with orderBy parameter
            var query = GetQueryable(false).Where(predicate);
            
            // Ordering logic would go here
            // This is a placeholder - actual implementation would depend on how you want to handle dynamic ordering
            
            return await query.Select(selector).Skip(skip).Take(take).ToListAsync(cancellationToken);
        }}

        public async Task<T?> GetSingleAsync(Expression<Func<T, bool>> predicate, bool tracking = false,
            CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).SingleOrDefaultAsync(predicate, cancellationToken);
        }}

        public async Task<TResult?> GetSingleAsync<TResult>(Expression<Func<T, bool>> predicate,
            Expression<Func<T, TResult>> selector, bool tracking = false, CancellationToken cancellationToken = default)
        {{
            return await GetQueryable(tracking).Where(predicate).Select(selector).SingleOrDefaultAsync(cancellationToken);
        }}

        public async Task<T?> FindByIdAsync(int id, CancellationToken cancellationToken = default)
        {{
            return await _dbSet.FindAsync(new object[] {{ id }}, cancellationToken);
        }}

        public async Task<T?> FindAsync(object[] keyValues, CancellationToken cancellationToken = default)
        {{
            return await _dbSet.FindAsync(keyValues, cancellationToken);
        }}

        public async Task<T> AddAsync(T entity, CancellationToken cancellationToken = default)
        {{
            var addedEntity = await _dbSet.AddAsync(entity, cancellationToken);
            addedEntity.State = EntityState.Added;
            return addedEntity.Entity;
        }}

        public async Task AddRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default)
        {{
            await _dbSet.AddRangeAsync(entities, cancellationToken);
        }}

        public Task UpdateAsync(T entity, CancellationToken cancellationToken = default)
        {{
            var updatedEntity = _dbSet.Update(entity);
            updatedEntity.State = EntityState.Modified;
            return Task.CompletedTask;
        }}

        public Task UpdateRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default)
        {{
            _dbSet.UpdateRange(entities);
            return Task.CompletedTask;
        }}

        public Task RemoveAsync(T entity, CancellationToken cancellationToken = default)
        {{
            var removedEntity = _dbSet.Remove(entity);
            removedEntity.State = EntityState.Deleted;
            return Task.CompletedTask;
        }}

        public Task RemoveRangeAsync(IEnumerable<T> entities, CancellationToken cancellationToken = default)
        {{
            _dbSet.RemoveRange(entities);
            return Task.CompletedTask;
        }}

        public Task<int> CountAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default)
        {{
            return GetQueryable().CountAsync(predicate, cancellationToken);
        }}

        public Task<bool> AnyAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default)
        {{
            return GetQueryable().AnyAsync(predicate, cancellationToken);
        }}

        public Task<bool> AllAsync(Expression<Func<T, bool>> predicate, CancellationToken cancellationToken = default)
        {{
            return GetQueryable().AllAsync(predicate, cancellationToken);
        }}

        private IQueryable<T> GetQueryable(bool tracking = false)
        {{
            return tracking ? _dbSet : _dbSet.AsNoTracking();
        }}
    }}
}}
"""